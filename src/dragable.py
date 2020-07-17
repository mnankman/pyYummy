import wx
import wx.lib.newevent

DragableHoverEvent, EVT_DRAGABLE_HOVER = wx.lib.newevent.NewEvent()
DragableReleaseEvent, EVT_DRAGABLE_RELEASE = wx.lib.newevent.NewEvent()

class DragablePanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.mOffset = (0,0)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_MOTION,  self.OnMouseMove)
        self.Bind(wx.EVT_LEFT_UP,  self.OnMouseUp)

    def OnMouseDown(self, event):
        self.CaptureMouse()
        mx,my = self.parent.ScreenToClient(wx.GetMousePosition())
        self.mOffset = self.ScreenToClient(wx.GetMousePosition())
        ox,oy = self.mOffset
        self.Move((mx-ox, my-oy))

    def OnMouseMove(self, event):
        if event.Dragging() and event.LeftIsDown():
            mx,my = self.parent.ScreenToClient(wx.GetMousePosition())
            ox,oy = self.mOffset
            self.Move((mx-ox, my-oy))
            hoverEvt = DragableHoverEvent(pos=(mx-ox, my-oy), obj=self)
            wx.PostEvent(self, hoverEvt)

    def OnMouseUp(self, event):
        if (self.HasCapture()): 
            self.ReleaseMouse()
            releaseEvt = DragableReleaseEvent(pos=self.GetPosition(), obj=self)
            wx.PostEvent(self, releaseEvt)


