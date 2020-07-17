import wx
from dragable import DragablePanel
from model import Tile

COLORS = ["#000000", "#3300CC", "#FF3300", "#FF6600"]

class TileWidget(DragablePanel):
    def __init__(self, parent, tile):
        DragablePanel.__init__(self, parent, size=(36, 50))

        self.tile = tile

        self.font = wx.Font(14, family = wx.FONTFAMILY_MODERN, style = 0, weight = 100, 
            underline = False, faceName ="", encoding = wx.FONTENCODING_DEFAULT) 

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.parent = parent
        self.SetBackgroundColour('#FFFFB8')
        self.SetForegroundColour(COLORS[self.tile.color])

        self.label = wx.StaticText(self, -1, str(self.tile.value))
        self.label.SetFont(self.font)
        hbox.Add(self.label, 0, wx.ALL|wx.ALIGN_CENTER)
        vbox.Add(hbox, 1, wx.ALL|wx.ALIGN_CENTER, 5)

        self.SetSizer(vbox)
