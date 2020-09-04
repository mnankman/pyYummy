import wx
import wx.lib.newevent

from log import Log
log = Log()

DraggableHoverEvent, EVT_DRAGGABLE_HOVER = wx.lib.newevent.NewEvent()
DraggableReleaseEvent, EVT_DRAGGABLE_RELEASE = wx.lib.newevent.NewEvent()

class DraggablePanel(wx.Panel):
    def __init__(self, parent, draggable=True, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.grandparent = parent.GetParent()
        self.mOffset = (0,0)
        self.__draggable__ = draggable
        self.__dragged__ = False
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_MOTION,  self.OnMouseMove)
        self.Bind(wx.EVT_LEFT_UP,  self.OnMouseUp)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.OnMouseCaptureLost)
        self.__posBeforeDrag__ = None
        self.__parentBeforeDrag__ = None

    def isBeingDragged(self):
        return self.__dragged__

    def isDraggable(self):
        return self.__draggable__

    def accept(self, newParent):
        log.debug(function=self.accept)
        self.Reparent(newParent)
        self.__posBeforeDrag__ = None
        self.__parentBeforeDrag__ = None

    def reject(self):
        log.debug(function=self.reject)
        self.restorePositionBeforeDrag()

    def restorePositionBeforeDrag(self):
        log.debug(function=self.restorePositionBeforeDrag, args=(self.__parentBeforeDrag__,self.__posBeforeDrag__))
        if self.__parentBeforeDrag__ != None and self.__posBeforeDrag__ != None:
            self.Reparent(self.__parentBeforeDrag__)
            self.Move(self.__posBeforeDrag__)
            self.GetParent().Refresh()
            self.__posBeforeDrag__ = None
            self.__parentBeforeDrag__ = None

    def dragStart(self):
        if not self.isBeingDragged():
            log.debug(function=self.dragStart)
            self.__posBeforeDrag__ = self.GetPosition()
            self.__parentBeforeDrag__ = self.GetParent()
            self.Reparent(self.grandparent)
            self.__dragged__ = True

    def drop(self):
        if self.isBeingDragged():
            log.debug(function=self.drop)
            if (self.HasCapture()): self.ReleaseMouse()
            self.__dragged__ = False
            releaseEvt = DraggableReleaseEvent(pos=self.GetPosition(), obj=self)
            wx.PostEvent(self, releaseEvt)

    def OnMouseDown(self, event):
        if not self.isDraggable(): return
        if not self.HasCapture(): self.CaptureMouse()
        self.mOffset = self.ScreenToClient(wx.GetMousePosition())

    def OnMouseMove(self, event):
        if not self.isDraggable(): return
        if event.Dragging() and event.LeftIsDown() and self.HasCapture():
            self.dragStart()
            #if not self.HasCapture(): self.CaptureMouse()
            mx,my = self.GetParent().ScreenToClient(wx.GetMousePosition())
            ox,oy = self.mOffset
            self.Move((mx-ox, my-oy))
            hoverEvt = DraggableHoverEvent(pos=(mx-ox, my-oy), obj=self)
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



