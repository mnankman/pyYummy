import wx
from draggable import DraggablePanel
import model

#COLORS = ["#000000", "#3300CC", "#FF3300", "#FF6600"]
COLORS = ["#333333", "#000066", "#CC0033", "#FF9933"]
RESOURCES="src/resource"

class TileWidget(DraggablePanel):
    yummyIcon = None
    def defaultSize():
        return (36,50)

    def __init__(self, parent, tile):
        DraggablePanel.__init__(self, parent, size=TileWidget.defaultSize(), style=wx.BORDER_RAISED|wx.CLIP_CHILDREN)

        if not TileWidget.yummyIcon:
            TileWidget.yummyIcon = wx.Bitmap(RESOURCES+"/yummy-icon-28-white.png")

        self.tile = tile

        self.font = wx.Font(14, family = wx.FONTFAMILY_MODERN, style = 0, weight = 100, 
            underline = False, faceName ="", encoding = wx.FONTENCODING_DEFAULT) 

        #self.SetBackgroundColour('#FFFFB8')
        #self.SetForegroundColour(COLORS[self.tile.color])
        #self.SetBackgroundColour(COLORS[self.tile.color])
        self.SetForegroundColour('White')

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        if not isinstance(self.tile, model.Joker):
            self.label = wx.StaticText(self, -1, str(self.tile.value))
            self.label.SetFont(self.font)
            hbox.Add(self.label, 0, wx.ALL|wx.ALIGN_CENTER)
    
        vbox.Add(hbox, 1, wx.ALL|wx.ALIGN_CENTER, 5)

        self.SetSizer(vbox)
        self.Bind(wx.EVT_PAINT,self.onPaint)

    def onPaint(self, event):
        event.Skip()
        #dc = wx.BufferedPaintDC(self)
        dc = wx.PaintDC(self)
        self.draw(dc)

    def draw(self,dc):
        #dc.SetPen(wx.Pen('Black', 1, wx.SOLID))
        #dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(COLORS[self.tile.color]))
        w,h = self.GetClientSize()
        dc.DrawRoundedRectangle(0,0,w,h,6)
        if isinstance(self.tile, model.Joker):
            iw,ih = TileWidget.yummyIcon.GetSize()
            dc.DrawBitmap(TileWidget.yummyIcon, int(0.5*(w-iw)), int(0.5*(h-ih)))


