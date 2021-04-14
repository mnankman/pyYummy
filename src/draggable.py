import wx
import wx.lib.newevent
import lib.log

DraggableHoverEvent, EVT_DRAGGABLE_HOVER = wx.lib.newevent.NewEvent()
DraggableReleaseEvent, EVT_DRAGGABLE_RELEASE = wx.lib.newevent.NewEvent()
DraggableAcceptEvent, EVT_DRAGGABLE_ACCEPT = wx.lib.newevent.NewEvent()

class DraggablePanel(wx.Panel):
    def __init__(self, parent, draggable=True, portable=True, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
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

    def isBeingDragged(self):
        return self.__dragged__

    def isDraggable(self):
        return self.__draggable__

    def isPortable(self):
        return self.__portable__

    def accept(self, newParent):
        log.debug(function=self.accept)
        if self.isPortable():
            self.Reparent(newParent)
        mx,my = self.GetParent().ScreenToClient(wx.GetMousePosition())
        ox,oy = self.mOffset
        self.Move((mx-ox, my-oy))
        self.__posBeforeDrag__ = None
        self.__parentBeforeDrag__ = None
        acceptEvt = DraggableAcceptEvent(pos=self.GetScreenPosition(), obj=self)
        wx.PostEvent(self, acceptEvt)

    def reject(self):
        log.debug(function=self.reject)
        self.restorePositionBeforeDrag()

    def restorePositionBeforeDrag(self):
        log.debug(function=self.restorePositionBeforeDrag, args=(self.__parentBeforeDrag__,self.__posBeforeDrag__))
        if self.__parentBeforeDrag__ != None and self.__posBeforeDrag__ != None:
            if self.isPortable(): self.Reparent(self.__parentBeforeDrag__)
            self.Move(self.__posBeforeDrag__)
            self.GetParent().Refresh()
            self.__posBeforeDrag__ = None
            self.__parentBeforeDrag__ = None

    def dragStart(self):
        if not self.isBeingDragged():
            log.debug(function=self.dragStart)
            self.__posBeforeDrag__ = self.GetPosition()
            self.__parentBeforeDrag__ = self.GetParent()
            if self.isPortable(): self.Reparent(self.getTopLevelPanel())
            self.__dragged__ = True

    def getTopLevelPanel(self):
        tlp = self.GetParent()
        while tlp.GetParent() and isinstance(tlp.GetParent(), wx.Panel):
            tlp = tlp.GetParent()
        return tlp

    def drop(self):
        if self.isBeingDragged():
            log.debug(function=self.drop)
            if (self.HasCapture()): self.ReleaseMouse()
            self.__dragged__ = False
            releaseEvt = DraggableReleaseEvent(pos=self.GetScreenPosition(), obj=self)
            wx.PostEvent(self, releaseEvt)
            
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
            self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

    def OnMouseLeave(self, event):
        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))


