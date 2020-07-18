import wx
import wx.lib.inspection

from tilewidget import TileWidget
import dragable
import model
from controller import Controller

ID_NEWGAME=101
ID_CONNECT=104
ID_EXIT=200
ID_SENDMESSAGE=500

class ButtonPanel(wx.Panel):    
    def __init__(self, parent, controller):
        super().__init__(parent=parent, size=(800,30))
        self.parent = parent
        self.controller = controller
        btnPlus = wx.Button(self, -1, "Plussss")
        btnPlus.Bind(wx.EVT_BUTTON, self.onPlusClicked)
        btnPlay = wx.Button(self, -1, "Plee")
        btnPlay.Bind(wx.EVT_BUTTON, self.onPlayClicked)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(btnPlus)
        hbox.Add(btnPlay)
        self.SetSizer(hbox)

    def onPlusClicked(self, event):
        self.parent.OnPlus(event)

    def onPlayClicked(self, event):
        self.controller.getCurrentGame().print()


def rectsOverlap(r1, r2):
    x1,y1,w1,h1 = r1
    x2,y2,w2,h2 = r2
    if (x1>=x2+w2) or (x1+w1<=x2) or (y1+h1<=y2) or (y1>=y2+h2):
        return False
    else:
        return True

class BoardPanel(wx.Panel):    
    def __init__(self, parent, controller):
        super().__init__(parent=parent, size=(800,500))
        self.parent = parent
        self.controller = controller
        self.SetBackgroundColour('#888888')
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_PAINT,self.onPaint)

    def onPaint(self, event):
        event.Skip()
        setpanels = self.getObjectsByType(SetPanel)
        for sp in setpanels:
            sx,sy,sw,sh = sp.GetRect()
            xOffset = 3
            for t in sp.set.tiles:
                tw = self.parent.findTileWidgetById(t)
                if tw:
                    w,h = tw.GetSize()
                    tw.Move((sx+xOffset, sy+3))
                    tw.Raise()
                    tw.Refresh()
                    xOffset = xOffset + w 

    def reset(self):
        for sp in self.getObjectsByType(SetPanel):
            sp.Destroy()

    def getObjectsByType(self, type):
        result = []
        children = self.GetChildren()
        for c in children:
            if isinstance(c, type):
                result.append(c)
        return result

    def findSetPanel(self, rect):
        children = self.GetChildren()
        setPnl = None
        for c in children:
            if isinstance(c, SetPanel):
                if rectsOverlap(rect,c.GetRect()):
                    setPnl = c
                    break
        return setPnl

    def triggerSetPanels(self, event):
        children = self.GetChildren()
        for c in children:
            if isinstance(c, SetPanel):
                c.onTileHover(event)

    def onTileHover(self, event):
        pos = event.pos
        self.triggerSetPanels(event)

    def onTileRelease(self, event):
        x,y = event.pos
        tile = event.obj.tile
        setPnl = self.findSetPanel(event.obj.GetRect())
        if setPnl:
            setPnl.onTileRelease(event)
        else:
            print ("released on board:", (x,y), event.obj.tile.toString())
            tile.move(self.controller.getCurrentGame().board)
            self.controller.getCurrentGame().print()
            setpanel = SetPanel(self, tile.container)
            w,h = event.obj.GetSize()
            setpanel.SetSize((w+6,h+10))
            setpanel.Move((x-3,y-4))
        event.obj.Raise()
        self.Refresh()

class SetPanel(dragable.DragablePanel):  
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
        dc = wx.PaintDC(self)
        self.draw(dc)

    def draw(self,dc):
        if self.highlight:
            dc.SetPen(wx.Pen(SetPanel.highlightPenColor, 1, wx.PENSTYLE_DOT))
        else:
            dc.SetPen(wx.Pen(SetPanel.normalPenColor, 1, wx.PENSTYLE_DOT))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        w,h = self.GetClientSize()
        dc.DrawRoundedRectangle(0,0,w,h,6)

    def onTileHover(self, event):
        if rectsOverlap(event.obj.GetRect(), self.GetRect()):
            self.highlight = True
        else:
            self.highlight = False
        self.Refresh()

    def onTileRelease(self, event):
        tile = event.obj.tile
        if tile.move(self.set):
            w,h = self.GetClientSize()
            self.SetSize(len(self.set.tiles)*36+6, h)
            self.Refresh()

class PlatePanel(wx.Panel):    
    def __init__(self, parent):
        super().__init__(parent=parent, size=(800,100))
        self.SetBackgroundColour('#CCCCCC')

class GamePanel(wx.Panel):    
    def __init__(self, parent, controller):
        super().__init__(parent=parent, size=(800,600))
        self.SetBackgroundColour('#CCCCCC')
        self.tiles = None
        self.game = None
        self.controller = controller
        
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.boardPanel = BoardPanel(self, self.controller)
        self.platePanel = PlatePanel(self)
        vbox.Add(self.boardPanel, 1, wx.EXPAND)
        vbox.Add(self.platePanel, 1, wx.EXPAND)

        self.newGame()
        self.SetSizer(vbox)

    def resetTileWidgets(self):
        if self.tiles != None:
            for tObj in self.tiles:
                tObj.Destroy()
        self.tiles = []

    def refreshTiles(self):
        self.controller.getCurrentGame().board.cleanUp()
        c = 0
        tx, ty = (0, 500)
        for t in self.player.plate.tiles.values():
            tile = self.findTileWidgetById(t.id())
            if not tile: 
                tile = TileWidget(self, t)
                self.tiles.append(tile)
                tile.Bind(dragable.EVT_DRAGABLE_HOVER, self.boardPanel.onTileHover)
                tile.Bind(dragable.EVT_DRAGABLE_RELEASE, self.boardPanel.onTileRelease)
            tile.Move((tx,ty))
            tx = tx+40

    def findTileWidgetById(self, tId):
        for c in self.GetChildren():
            if isinstance(c, TileWidget):
                if tId==c.tile.id():
                    return c
        return None
            
    def newGame(self):
        self.controller.newGame(2)
        self.controller.addPlayer("player1")
        self.player = self.controller.getPlayer("player1")
        self.boardPanel.reset()
        self.resetTileWidgets()
        self.refreshTiles()

    def getGame(self):
        return self.game

    def plus(self):
        if self.player != None:
            self.player.pickTile()
            self.refreshTiles()
            self.Refresh()


class MainWindow(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Yummy')

        iconFile = "yummy-icon-28-white.png"
        icon = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.controller = Controller()

        self.buttonPanel = ButtonPanel(self, self.controller)
        self.gamePanel = GamePanel(self, self.controller)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.buttonPanel)
        self.sizer.Add(self.gamePanel, 1, wx.EXPAND)

        self.create_menu()
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Centre()
        self.Show()

    def create_menu(self):
        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        fileMenu.Append(ID_NEWGAME, "&Start new game", "Start a new game of Yummy")
        fileMenu.Append(ID_EXIT, "E&xit", "Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        self.Bind(event=wx.EVT_MENU, handler=self.OnNewGame, id=ID_NEWGAME)
        self.Bind(event=wx.EVT_MENU, handler=self.OnExit, id=ID_EXIT)

    def onMessageReceived(self, payload):
        self.chatPanel.addMessage(payload[1])

    def OnExit(self, e):
        #answer = self.exitDialog.ShowModal()
        #if answer == wx.ID_YES:
        if True:
            self.Close(True) 

    def OnNewGame(self, e):
        self.gamePanel.newGame()

    def OnPlus(self, e):
        self.gamePanel.plus()


if __name__ == '__main__':
    app = wx.App()
    w = MainWindow()
#    wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()

