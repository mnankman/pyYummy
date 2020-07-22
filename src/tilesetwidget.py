import wx
from dragable import DragablePanel
import model
import util

class TileSetWidget(DragablePanel):  
    normalPenColor = 'Black'
    highlightPenColor = 'White'
    def __init__(self, parent, set):
#        super().__init__(parent=parent, style=wx.TRANSPARENT_WINDOW)
        super().__init__(parent=parent)
        self.set = set
        self.highlight = False
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.Bind(wx.EVT_PAINT,self.onPaint)

    def onPaint(self, event):
        event.Skip()
        #dc = wx.BufferedPaintDC(self)
        if self.set.isModified():
            w,h = self.GetClientSize()
            self.SetSize(len(self.set.getTiles())*36+6, h)
        dc = wx.PaintDC(self)
        self.draw(dc)

    def draw(self,dc):
        if self.highlight:
            dc.SetPen(wx.Pen(TileSetWidget.highlightPenColor, 1, wx.PENSTYLE_DOT))
        else:
            dc.SetPen(wx.Pen(TileSetWidget.normalPenColor, 1, wx.PENSTYLE_DOT))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        w,h = self.GetClientSize()
        dc.DrawRoundedRectangle(0,0,w,h,6)

    def onTileHover(self, event):
        if util.rectsOverlap(event.obj.GetRect(), self.GetRect()) and self.set.tileFitPosition(event.obj.tile)>0:
            self.highlight = True
        else:
            self.highlight = False
        self.Refresh()

    def onTileRelease(self, event):
        tile = event.obj.tile
        if tile.move(self.set):
            w,h = self.GetClientSize()
            self.SetSize(len(self.set.getTiles())*36+6, h)
            self.Refresh()


