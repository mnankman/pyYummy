import wx
from draggable import DraggablePanel
import model
from styler import PaintStyler

from log import Log
log = Log()

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
        self.Bind(wx.EVT_PAINT,self.onPaint)

    def onPaint(self, event):
        event.Skip()
        dc = wx.PaintDC(self)
        self.drawBackground(dc)
        self.drawFace(dc)

    def drawBackground(self, dc):
        self.paintStyler.select(STYLES[self.color], dc)
        w,h = self.GetClientSize()
        dc.DrawRoundedRectangle(1,1,w-1,h-1,3)
        gc = wx.GraphicsContext.Create(dc)
        brushColor = dc.GetBrush().GetColour()
        if gc:
            gbrush = gc.CreateLinearGradientBrush(-10,-20,w,h,
                brushColor.ChangeLightness(90), 
                brushColor.ChangeLightness(120))
            gc.SetBrush(gbrush)
            path = gc.CreatePath()
            path.AddRoundedRectangle(2,5,w-2,h-12,6)
            gc.DrawPath(path)
      

    def drawFace(self, dc):
        self.paintStyler.select(STYLES[self.color], dc)
        w,h = self.GetClientSize()
        if isinstance(self.tile, model.Joker):
            iw,ih = TileWidget.yummyIcon.GetSize()
            dc.DrawBitmap(TileWidget.yummyIcon, int(0.5*(w-iw)), int(0.5*(h-ih)))
        else:
            tw,th = dc.GetTextExtent(self.valueStr)
            tx,ty = (0.5*(w-tw), 0.5*(h-th))
            dc.DrawText(self.valueStr, tx, ty)


