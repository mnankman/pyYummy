import wx
from draggable import DraggablePanel
import model
import lib.log
from styler import PaintStyler

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
        #dc.DrawRoundedRectangle(1,1,w-1,h-1,3)
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            brushColor = dc.GetBrush().GetColour()

            gbrush = gc.CreateLinearGradientBrush(0,h,0,0,
                brushColor.ChangeLightness(90), 
                brushColor.ChangeLightness(120))
            gc.SetBrush(gbrush)
            path = gc.CreatePath()
            path.AddRoundedRectangle(1,1,w-1,h-1,3)
            gc.DrawPath(path)

            gbrush = gc.CreateLinearGradientBrush(0,0,0,h,
                brushColor.ChangeLightness(90), 
                brushColor.ChangeLightness(120))
            gc.SetBrush(gbrush)
            path = gc.CreatePath()
            path.AddRoundedRectangle(4,6,w-8,h-14,6)
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


