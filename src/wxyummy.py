import wx
from wxasync import WxAsyncApp
import asyncio

import wx.lib.inspection

import styles
from tilewidget import TileWidget
from tilesetwidget import TileSetWidget
from gamepanels import BoardPanel, GamePanel, PlatePanel
import draggable
import model
from controller import Controller
import util
import log

RESOURCES="src/resource"

ID_NEWGAME=101
ID_SAVEGAME=102
ID_LOADGAME=103
ID_CONNECT=104
ID_EXIT=200
ID_SENDMESSAGE=500
ID_SHOWINSPECTIONTOOL=600

class ButtonBar(wx.Panel):    
    def __init__(self, parent, controller, player):
        super().__init__(parent=parent, size=(800,45))
        self.parent = parent
        self.controller = controller
        self.player = player

        self.btnFacePlay = wx.Bitmap(RESOURCES+"/yummy-btnface-play-28-white.png")
        self.btnFacePlus = wx.Bitmap(RESOURCES+"/yummy-btnface-plus-28-white.png")

        btnPlus = wx.Button(self, -1, "", size=(40, 40), style=wx.NO_BORDER)
        btnPlus.SetBackgroundColour("#333333")
        btnPlus.SetBitmap(self.btnFacePlus)
        btnPlus.Bind(wx.EVT_BUTTON, self.onUserPlus)

        btnPlay = wx.Button(self, -1, "", size=(40, 40), style=wx.NO_BORDER)
        btnPlay.SetBackgroundColour("#333333")
        btnPlay.SetBitmap(self.btnFacePlay)
        btnPlay.Bind(wx.EVT_BUTTON, self.onUserPlay)

        btnSort = wx.Button(self, -1, "123", size=(40, 40), style=wx.NO_BORDER)
        btnSort.SetBackgroundColour("#333333")
        btnSort.SetForegroundColour('White')
        #btnSort.SetBitmap(self.btnFaceSort)
        btnSort.Bind(wx.EVT_BUTTON, self.onUserToggleSort)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(btnPlus, 0, wx.ALL, 2)
        hbox.Add(btnPlay, 0, wx.ALL, 2)
        hbox.Add(btnSort, 0, wx.ALL, 2)
        self.SetSizer(hbox)

    def checkPlayerTurn(self):
        if not self.controller.isCurrentPlayer(self.player):
            dlg = wx.MessageDialog(self, "It is not your turn!", 
                            caption="Message", style=wx.OK|wx.CENTRE, pos=wx.DefaultPosition)
            dlg.ShowModal()
            return False
        return True

    def onUserPlus(self, e):
        if self.checkPlayerTurn():
            self.controller.pick()

    def onUserPlay(self, e):
        if self.checkPlayerTurn():
            self.controller.commit()
            self.controller.getCurrentGame().print()

    def onUserToggleSort(self, event):
        self.parent.onUserToggleSort(event)

class GameWindow(wx.Frame):
    def __init__(self, controller, playerName):
        super().__init__(parent=None, title=playerName)
        iconFile = RESOURCES+"/yummy-icon-28-white.png"
        icon = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        
        self.controller = controller

        game = self.controller.getCurrentGame()
        player = game.getPlayerByName(playerName)
        assert isinstance(player, model.Player)

        self.gamePanel = GamePanel(self, game, player)
        #self.controller.model.subscribe(self.gamePanel, "msg_new_game", self.gamePanel.onMsgNewGame)
        self.controller.model.subscribe(self.gamePanel, "msg_game_loaded", self.gamePanel.onMsgGameLoaded)
        #self.controller.model.subscribe(self.gamePanel, "msg_new_player", self.gamePanel.onMsgNewPlayer)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(ButtonBar(self, self.controller, player))
        self.sizer.Add(self.gamePanel, 1, wx.EXPAND)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Centre()

    def onUserToggleSort(self, e):
        self.gamePanel.toggleSort()

class MainWindow(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Yummy')

        styles.init()

        iconFile = RESOURCES+"/yummy-icon-28-white.png"
        icon = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.controller = Controller()
        self.controller.model.subscribe(self, "msg_new_player", self.onMsgNewPlayer)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.create_menu()
        self.SetSizer(self.sizer)
        #self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Centre()
        #self.SetClientSize(400,300)
        self.Show()

    def create_menu(self):
        menuBar = wx.MenuBar()
        debugMenu = wx.Menu()
        debugMenu.Append(ID_SHOWINSPECTIONTOOL, "&Inspection tool", "Show the WX Inspection Tool")
        fileMenu = wx.Menu()
        fileMenu.Append(ID_NEWGAME, "Start &new game", "Start a new game of Yummy")
        fileMenu.Append(ID_SAVEGAME, "&Save game", "Save this game")
        fileMenu.Append(ID_LOADGAME, "&Load game", "Load game")
        fileMenu.Append(ID_EXIT, "E&xit", "Exit")
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(debugMenu, "&Debug")
        self.SetMenuBar(menuBar)

        self.Bind(event=wx.EVT_MENU, handler=self.onUserNewGame, id=ID_NEWGAME)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserSaveGame, id=ID_SAVEGAME)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserLoadGame, id=ID_LOADGAME)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserExit, id=ID_EXIT)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserShowInspectionTool, id=ID_SHOWINSPECTIONTOOL)

    def onMsgNewPlayer(self, payload):
        log.debug(function=self.onMsgNewPlayer, args=payload)
        player = payload["player"]
        btnPlayer = wx.Button(self, -1, player.getName(), size=(100, 20), )
        btnPlayer.Bind(wx.EVT_BUTTON, self.onUserPlayerClick)
        self.sizer.Add(btnPlayer)
        self.SetClientSize(400,300)
        #self.Refresh()

    def onUserPlayerClick(self, e):
        playerName = e.GetEventObject().GetLabel() 
        gw = GameWindow(self.controller, playerName)
        gw.Show()

    def onUserExit(self, e):
        #answer = self.exitDialog.ShowModal()
        #if answer == wx.ID_YES:
        if True:
            self.Close(True) 

    def onUserNewGame(self, e):
        self.controller.newGame(2)
        self.controller.addPlayer("player1")
        self.controller.addPlayer("player2")
        self.controller.start()

    def onUserSaveGame(self, e):
        # Create open file dialog
        dlg = wx.FileDialog(self, "Save", "", "", 
            "Yummy files (*.yummy)|*.yummy", 
            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        path = dlg.GetPath()
        dlg.Destroy()

        self.controller.saveGame(path)

    def onUserLoadGame(self, e):
        # Create open file dialog
        dlg = wx.FileDialog(self, "Open", "", "", 
            "Yummy files (*.yummy)|*.yummy", 
            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        path = dlg.GetPath()
        dlg.Destroy()
       
        self.controller.loadGame(path)

    def onUserShowInspectionTool(self, e):
        wx.lib.inspection.InspectionTool().Show()



def start():
    app = WxAsyncApp()
    w = MainWindow()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(app.MainLoop())
    finally:
        loop.stop()
        loop.close()

if __name__ == '__main__':
    start()
