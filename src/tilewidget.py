import wx
from draggable import DraggablePanel
import model
from styler import PaintStyler

#COLORS = ["#000000", "#3300CC", "#FF3300", "#FF6600"]
COLORS = ["#333333", "#000066", "#CC0033", "#FF9933"]
RESOURCES="src/resource"
STYLES = ["TileWidget:black", "TileWidget:blue", "TileWidget:red", "TileWidget:orange"]

class TileWidget(DraggablePanel):
    yummyIcon = None
    def defaultSize():
        return (36,50)

    def __init__(self, parent, tile):
        DraggablePanel.__init__(self, parent, size=TileWidget.defaultSize(), style=wx.CLIP_CHILDREN)

        if not TileWidget.yummyIcon:
            TileWidget.yummyIcon = wx.Bitmap(RESOURCES+"/yummy-icon-28-white.png")

        self.paintStyler = PaintStyler()
        self.tile = tile
        self.color = self.tile.getColor()
        self.valueStr = str(self.tile.getValue())
        self.brush = wx.Brush(COLORS[self.tile.getColor()])
        self.Bind(wx.EVT_PAINT,self.onPaint)

    def onPaint(self, event):
        event.Skip()
        dc = wx.PaintDC(self)
        self.draw(dc)

    def draw(self,dc):
        self.paintStyler.select(STYLES[self.color], dc)
        w,h = self.GetClientSize()
        dc.DrawRoundedRectangle(1,1,w-1,h-1,6)
        if isinstance(self.tile, model.Joker):
            iw,ih = TileWidget.yummyIcon.GetSize()
            dc.DrawBitmap(TileWidget.yummyIcon, int(0.5*(w-iw)), int(0.5*(h-ih)))
        else:
            tw,th = dc.GetTextExtent(self.valueStr)
            tx,ty = (0.5*(w-tw), 0.5*(h-th))
            dc.DrawText(self.valueStr, tx, ty)


