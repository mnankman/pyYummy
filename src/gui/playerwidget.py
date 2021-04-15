import wx
from lib import log
from gui.styler import PaintStyler

RESOURCES="src/resource"

class PlayerWidget(wx.Panel):
    yummyIcon = None
    DEFAULTSIZE = (100,12)

    def __init__(self, parent, player):
        super().__init__(parent, size=PlayerWidget.DEFAULTSIZE, style=wx.CLIP_CHILDREN)
        self.player = None

        if not PlayerWidget.yummyIcon:
            PlayerWidget.yummyIcon = wx.Bitmap(RESOURCES+"/yummy-icon-28-white.png")

        self.paintStyler = PaintStyler()
        self.Bind(wx.EVT_PAINT,self.onPaint)

        self.reset(player)

    def Destroy(self):
        self.set.unsubscribe("msg_object_modified", self)
        super().Destroy()

    def reset(self, player=None):
        if self.player:
            self.player.unsubscribe("msg_object_modified", self)
        self.player = player
        if self.player != None:
            self.player.subscribe(self, "msg_object_modified", self.onMsgPlayerModified)
    
    def playerInfo(self):
        return self.player.getName() + "(" + str(self.player.getPlate().getSize()) + ")"

    def onPaint(self, event):
        event.Skip()
        dc = wx.PaintDC(self)
        self.drawBackground(dc)
        self.drawFace(dc)

    def style(self):
        return "PlayerWidget:" + ("playing" if self.player.isPlayerTurn() else "waiting")

    def drawBackground(self, dc):
        self.paintStyler.select(self.style(), dc)
        w,h = self.GetClientSize()
        dc.DrawRoundedRectangle(1,1,w-1,h-1,3)     

    def drawFace(self, dc):
        self.paintStyler.select(self.style(), dc)
        w,h = self.GetClientSize()
        #iw,ih = PlayerWidget.yummyIcon.GetSize()
        #dc.DrawBitmap(PlayerWidget.yummyIcon, 3, int(0.5*(h-ih)))
        txt = self.playerInfo()
        tw,th = dc.GetTextExtent(txt)
        tx,ty = (3, 0.5*(h-th))
        dc.DrawText(txt, tx, ty)

    def onMsgPlayerModified(self, payload):
        #log.debug(function=self.onMsgPlayerModified, args=payload)
        self.Refresh()

