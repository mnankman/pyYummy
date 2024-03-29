import wx
import wx.lib.newevent
from lib import log, util
from gui.styler import PaintStyler

DraggableHoverEvent, EVT_DRAGGABLE_HOVER = wx.lib.newevent.NewEvent()
DraggableReleaseEvent, EVT_DRAGGABLE_RELEASE = wx.lib.newevent.NewEvent()
DraggableAcceptEvent, EVT_DRAGGABLE_ACCEPT = wx.lib.newevent.NewEvent()

class DraggableControl(wx.Panel):
    """
    This class provides all the functionality needed for dragging and dropping. 
    Instances of this class emit the events: DraggableHoverEvent, DraggableReleaseEvent and DraggableAcceptEvent. 
    Droptargets need to bind to these events when they need to respond to these events.
    """
    def __init__(self, parent, draggable=True, portable=True, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grandparent = parent.GetParent()
        self.mOffset = (0,0) #the relative pos within the dragged object where the mouse was clicked
        self.__draggable__ = draggable
        self.__dragged__ = False
        self.__portable__ = portable #a portable draggable panel can be dragged out of the container
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_MOTION,  self.OnMouseMove)
        self.Bind(wx.EVT_LEFT_UP,  self.OnMouseUp)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.OnMouseCaptureLost)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)
        self.__posBeforeDrag__ = None
        self.__parentBeforeDrag__ = None
        self.__dragPlane__ = None

    def __AddChild(self, newChild):
        log.debug(function=self.AddChild, args=newChild)
        children = []
        for c in self.GetChildren():
            children.append(c)
        for c in children:
            self.RemoveChild(c)
        super().AddChild(newChild)
        for c in children:
            super().AddChild(c)

    def isBeingDragged(self):
        return self.__dragged__

    def isDraggable(self):
        return self.__draggable__

    def isPortable(self):
        return self.__portable__

    def accept(self, newParent):
        """
        This method is called by a drop target when it accepts this instance when it is dropped.
        Parameters:
        - newParent: the Drop Target that accepts this instance as a new child object
        Generates event: DraggableAcceptEvent
        """
        log.debug(function=self.accept, args=(self.GetName(), newParent.GetName()))
        if self.isPortable():
            self.Reparent(newParent)
        mx,my = self.GetParent().ScreenToClient(wx.GetMousePosition())
        ox,oy = self.mOffset
        self.Move((mx-ox, my-oy))
        self.__posBeforeDrag__ = None
        self.__parentBeforeDrag__ = None
        acceptEvt = DraggableAcceptEvent(pos=self.GetScreenPosition(), obj=self)
        wx.PostEvent(self, acceptEvt)

    def reject(self, restore=False):
        """
        This method is called by a drop target when it does not accept this instance when it is dropped.
        Parameters: 
        - restore: indicates whether this instance should be moved back to the position it was dragged from (default is False)
        """
        log.debug(function=self.reject, args=self.GetName())
        if restore:
            self.restorePositionBeforeDrag()

    def restorePositionBeforeDrag(self):
        """
        Restores the position and parent of this instance to the position within that parent's rectangle, before it was dragged.
        """
        log.debug(function=self.restorePositionBeforeDrag, args=(self.__parentBeforeDrag__,self.__posBeforeDrag__))
        if self.__parentBeforeDrag__ != None and self.__posBeforeDrag__ != None:
            if self.isPortable(): self.Reparent(self.__parentBeforeDrag__)
            self.Move(self.__posBeforeDrag__)
            self.GetParent().Refresh()
            self.__posBeforeDrag__ = None
            self.__parentBeforeDrag__ = None

    def dragStart(self):
        """
        THis method is called when this draggable gets mouse capture and is being dragged.
        This will Initiate the dragging state for this instance. It's original parent and the position within that parent is stored.
        If this instance is a portable draggable (i.e. it can be dragged out of a panel and into another panel), then a temporary, 
        transparent drag plane is created that becomes the parent during the period this instance is dragged. When the draggable is 
        released, the drag plane is destroyed.
        """
        if not self.isBeingDragged():
            log.debug(function=self.dragStart, args=self.GetName())
            self.__posBeforeDrag__ = self.GetPosition()
            self.__parentBeforeDrag__ = self.GetParent()
            if self.isPortable(): 
                self.__dragPlane__ = DragPlane(self.getTopLevelPanel(), self)
            self.__dragged__ = True
            self.Raise()

    def destroyDragPanel(self):
        """
        Destroys the temporary drag panel if it is active.
        """
        log.debug(function=self.destroyDragPanel, args=self.GetName())
        if self.__dragPlane__:
            self.__dragPlane__.Destroy()
            del self.__dragPlane__

    def getTopLevelPanel(self):
        """
        Returns the top most parent that is an instance of wx.Panel for this DraggableControl instance.
        """
        tlp = self.GetParent()
        while tlp.GetParent() and isinstance(tlp.GetParent(), wx.Panel):
            tlp = tlp.GetParent()
        log.debug(function=self.getTopLevelPanel, args=self.GetName(), returns=tlp.GetName())
        return tlp

    def drop(self):
        """
        This method is called when the draggable loses mouse capture
        """
        if self.isBeingDragged():
            log.debug(function=self.drop, args=self.GetName())
            if (self.HasCapture()): self.ReleaseMouse()
            self.__dragged__ = False
            self.destroyDragPanel()
            releaseEvt = DraggableReleaseEvent(pos=self.GetScreenPosition(), obj=self)
            wx.PostEvent(self, releaseEvt)
            self.Refresh()
            
    def OnMouseDown(self, event):
        if not self.isDraggable(): return
        if not self.HasCapture(): self.CaptureMouse()
        self.mOffset = self.ScreenToClient(wx.GetMousePosition())

    def OnMouseMove(self, event):
        if not self.isDraggable(): return
        #log.debug(function=self.OnMouseMove, args=(event.Dragging(),event.LeftIsDown(), self.HasCapture()))
        if event.Dragging() and event.LeftIsDown() and self.HasCapture():
            self.dragStart()
            mx,my = self.GetParent().ScreenToClient(wx.GetMousePosition())
            ox,oy = self.mOffset
            self.Move((mx-ox, my-oy))
            hoverEvt = DraggableHoverEvent(pos=self.GetScreenPosition(), obj=self)
            wx.PostEvent(self, hoverEvt)

    def OnMouseUp(self, event):
        if not self.isDraggable(): return
        log.debug(function=self.OnMouseUp, args=event)
        self.drop()

    def OnMouseCaptureLost(self, event):
        if not self.isDraggable(): return
        log.debug(function=self.OnMouseCaptureLost, args=event)
        if (self.isBeingDragged()): 
            self.__dragged__ = False
            self.restorePositionBeforeDrag()

    def OnMouseEnter(self, event):
        if self.isDraggable():
            self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

    def OnMouseLeave(self, event):
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

class DragPlane(wx.Panel):
    """
    An instance of this class represents a temporary "drag plane" for a portable draggable
    """
    def __init__(self, parent, draggableControl):
        super().__init__(parent, name=draggableControl.GetName()+"_dragplane", size=parent.GetSize(), style=wx.TRANSPARENT_WINDOW)
        self.__parent__ = parent
        self.__dp__ = draggableControl
        draggableControl.Reparent(self)
        self.Bind(wx.EVT_PAINT,self.onPaint)
        self.paintStyler = PaintStyler()

    def Destroy(self):
        self.__dp__.Reparent(self.__parent__)
        super().Destroy()

    def onPaint(self, event):
        event.Skip()
        self.draw(wx.PaintDC(self))

    def draw(self, dc):
        self.paintStyler.select("DragPlane:normal", dc)
        w,h = self.GetClientSize()
        dc.DrawRectangle(0,0,w,h)

class DraggableEventListener():
    """
    THis class provides the basic interface for DraggableEvent listeners 
    """    
    def bindToDraggableEvents(self, draggable):
        """
        """
        log.debug(function=self.bindToDraggableEvents, args=(self.GetName(), draggable.GetName()))
        assert draggable
        assert isinstance(draggable, DraggableControl)
        draggable.Bind(EVT_DRAGGABLE_HOVER, self.onDraggableHover)
        draggable.Bind(EVT_DRAGGABLE_RELEASE, self.onDraggableRelease)
        draggable.Bind(EVT_DRAGGABLE_ACCEPT, self.onDraggableAccept)  

    def onDraggableHover(self, event):
        """
        """
        pass
    
    def onDraggableRelease(self, event):
        """
        """
        pass
    
    def onDraggableAccept(self, event):
        """
        """
        pass

class DraggableDropTarget(DraggableControl, DraggableEventListener):
    """
    Instances of this class can respond to draggable events. Since they also derive from DraggableCOntrol, 
    these instances can be dragged and dropped themselvers too.
    """
    def __init__(self, parent, draggable=False, portable=False, *args, **kwargs):
        super().__init__(parent, draggable, portable, *args, **kwargs)
        self.parent = parent
        self.__draggableOver__ = False
        self.__mouseOver__ = False
        self.Bind(wx.EVT_PAINT,self.onPaint)
        self.Bind(wx.EVT_ENTER_WINDOW, self.onMouseEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
        self.paintStyler = PaintStyler()

    def getObjectsByType(self, type):
        """
        """
        result = []
        children = self.GetChildren()
        for c in children:
            if isinstance(c, type):
                result.append(c)
        return result

    def isMouseOver(self):
        """
        """
        return self.__mouseOver__

    def isDraggableOver(self):
        """
        """
        return self.__draggableOver__
    
    def onMouseEnter(self, event):
        self.__mouseOver__ = True
        self.Refresh()
        event.Skip()

    def onMouseLeave(self, event):
        self.__mouseOver__ = False
        self.Refresh()
        event.Skip()

    def onDraggableHover(self, event):
        if util.rectsOverlap(event.obj.GetScreenRect(), self.GetScreenRect()):
            self.__draggableOver__ = True
            event.obj.Refresh()
        else:
            self.__draggableOver__ = False
        self.Refresh()
        event.Skip()

    def onDraggableRelease(self, event):
        log.debug(function=self.onDraggableRelease, args=self.GetName())
        event.Skip(False)
        assert isinstance(event.obj, DraggableControl)
        if util.rectsOverlap(event.obj.GetScreenRect(), self.GetScreenRect()):
            event.obj.accept(self)
            self.__draggableOver__ = False
            self.Refresh()
        else:
            event.obj.reject()
            event.Skip(True)

    def onDraggableAccept(self, event):
        self.Refresh()

    def onPaint(self, event):
        event.Skip()
        dc = wx.PaintDC(self)
        self.draw(dc)

    def getLabel(self):
        lbl = """{name}({children})"""
        return lbl.format(name=self.GetName(), children=len(self.GetChildren()))

    def draw(self, dc):
        if self.__draggableOver__:
            self.paintStyler.select("DraggableDropTarget:highlight", dc)
        else:
            if self.__mouseOver__:
                self.paintStyler.select("DraggableDropTarget:mouseOver", dc)
            else:
                self.paintStyler.select("DraggableDropTarget:normal", dc)
        w,h = self.GetClientSize()
        lbl = self.getLabel()
        tw,th = dc.GetTextExtent(lbl)
        tx,ty = (0.5*(w-tw), (h-th-5))
        dc.DrawText(lbl, tx, ty)
        dc.DrawRectangle(0,0,w,h)

class DraggableDropFrame(wx.Frame, DraggableEventListener):
    def __init__(self, parent, *args, **kwargs):
        wx.Frame.__init__(self, parent, *args, **kwargs)

    def onDraggableRelease(self, event):
        """
        """
        log.debug(function=self.onDraggableRelease, args=self.GetName())
        event.obj.reject(True)

class NoneSizer(wx.Sizer):
    def __init__(self):
        super().__init__()

    def CalcMin(self):
        log.debug(function=self.CalcMin)
        return self.GetContainingWindow().GetSize()

    def RepositionChildren(self, minSize):
        pass