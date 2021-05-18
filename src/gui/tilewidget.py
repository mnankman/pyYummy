import wx
from base import model
from lib import log
from gui.draggable import DraggablePanel
from gui.styler import PaintStyler

RESOURCES="src/resource"
STYLES = ["TileWidget:black", "TileWidget:blue", "TileWidget:red", "TileWidget:orange"]

class TileWidget(DraggablePanel):
    yummyIcon = None
    DEFAULTSIZE = (36,50)

    def __init__(self, parent, tile):
        DraggablePanel.__init__(self, parent, name=tile.toString(), size=TileWidget.DEFAULTSIZE, style=wx.CLIP_CHILDREN)

        if not TileWidget.yummyIcon:
            TileWidget.yummyIcon = wx.Bitmap(RESOURCES+"/yummy-icon-28-white.png")

        self.paintStyler = PaintStyler()
        self.tile = tile
        self.color = self.tile.getColor()
        self.valueStr = str(self.tile.getValue())
        self.Bind(wx.EVT_PAINT,self.onPaint)

    def getZoomFactor(self):
        try: 
            return self.GetParent().getZoomFactor()
        finally:
            return 1

    def adjustSize(self, size, zf):
        return (size[0]*zf,size[1]*zf)

    def onPaint(self, event):
        event.Skip()
        dc = wx.PaintDC(self)
        zf = self.getZoomFactor()
        self.drawBackground(dc, zf)
        self.drawFace(dc, zf)

    def drawBackground(self, dc, zf):
        self.paintStyler.select(STYLES[self.color], dc)
        w,h = self.adjustSize(self.GetClientSize(), zf)
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
      

    def drawFace(self, dc, zf):
        self.paintStyler.select(STYLES[self.color], dc)
        w,h = self.adjustSize(self.GetClientSize(), zf)
        if isinstance(self.tile, model.Joker):
            iw,ih = self.adjustSize(TileWidget.yummyIcon.GetSize(), zf)
            dc.DrawBitmap(TileWidget.yummyIcon, int(0.5*(w-iw)), int(0.5*(h-ih)))
        else:
            tw,th = self.adjustSize(dc.GetTextExtent(self.valueStr), zf)
            tx,ty = (0.5*(w-tw), 0.5*(h-th))
            dc.DrawText(self.valueStr, tx, ty)


