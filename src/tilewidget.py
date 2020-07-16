import wx

COLORS = ["#000000", "#3300CC", "#FF3300", "#FF6600"]

class TileWidget(wx.Panel):
    def __init__(self, parent, value, color):
        wx.Panel.__init__(self, parent, size=(36, 50))

        self.value = value

        self.font = wx.Font(14, family = wx.FONTFAMILY_MODERN, style = 0, weight = 100, 
            underline = False, faceName ="", encoding = wx.FONTENCODING_DEFAULT) 

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.parent = parent
        self.SetBackgroundColour('#FFFFB8')
        self.SetForegroundColour(COLORS[color])

        self.label = wx.StaticText(self, -1, str(self.value))
        self.label.SetFont(self.font)
        hbox.Add(self.label, 0, wx.ALL|wx.ALIGN_CENTER)
        vbox.Add(hbox, 1, wx.ALL|wx.ALIGN_CENTER, 5)

        self.SetSizer(vbox)

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

    def OnMouseUp(self, event):
        if (self.HasCapture()): 
            self.ReleaseMouse()


