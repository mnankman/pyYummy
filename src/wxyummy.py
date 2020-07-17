import wx
from tilewidget import TileWidget
import dragable
import model

ID_NEWGAME=101
ID_CONNECT=104
ID_EXIT=200
ID_SENDMESSAGE=500

class ButtonPanel(wx.Panel):    
    def __init__(self, parent):
        super().__init__(parent=parent, size=(800,30))
        self.parent = parent
        btnPlus = wx.Button(self, -1, "Plussss")
        btnPlus.Bind(wx.EVT_BUTTON, self.onPlusClicked)
        btnPlay = wx.Button(self, -1, "Plee")
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(btnPlus)
        hbox.Add(btnPlay)
        self.SetSizer(hbox)

    def onPlusClicked(self, event):
        self.parent.OnPlus(event)


class BoardPanel(wx.Panel):    
    def __init__(self, parent):
        super().__init__(parent=parent, size=(800,500))
        self.SetBackgroundColour('#888888')
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

class PlatePanel(wx.Panel):    
    def __init__(self, parent):
        super().__init__(parent=parent, size=(800,100))
        self.SetBackgroundColour('#CCCCCC')

class GamePanel(wx.Panel):    
    def __init__(self, parent):
        super().__init__(parent=parent, size=(800,600))
        self.SetBackgroundColour('#CCCCCC')
        self.tiles = None
        
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.boardPanel = BoardPanel(self)
        self.platePanel = PlatePanel(self)
        vbox.Add(self.boardPanel, 1, wx.EXPAND)
        vbox.Add(self.platePanel, 1, wx.EXPAND)

        self.newGame()
        self.SetSizer(vbox)

    def initTiles(self):
        if self.tiles != None:
            for tObj in self.tiles:
                tObj.Destroy()

        self.tiles = []
        c = 0
        tx, ty = (0, 500)
        for t in self.player.plate.tiles.values():
            tile = TileWidget(self, t)
            tile.Move((tx,ty))
            self.tiles.append(tile)
            tx = tx+40
            tile.Bind(dragable.EVT_DRAGABLE_HOVER, self.onTileHover)
            tile.Bind(dragable.EVT_DRAGABLE_RELEASE, self.onTileRelease)

    def onTileHover(self, event):
        pos = event.pos
        print ("hover:", pos)

    def onTileRelease(self, event):
        pos = event.pos
        print ("released:", pos, event.obj.tile.toString())
            
    def newGame(self):
        self.game = model.Game(2)
        self.game.addPlayer("player1")
        self.player = self.game.getPlayer("player1")
        self.initTiles()

    def plus(self):
        if self.player != None:
            self.player.pickTile()
            self.initTiles()


class MainWindow(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='WxYummy')

        self.buttonPanel = ButtonPanel(self)
        self.gamePanel = GamePanel(self)

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
    app.MainLoop()

