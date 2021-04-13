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
from gameserver import GameServer
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
        self.playerName = player.getName()

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
        player = self.controller.getCurrentGame().getPlayerByName(self.playerName)
        if not player.isPlayerTurn():
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
        else:
            self.controller.revert()
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

        self.game = self.controller.getCurrentGame()
        self.player = self.game.getPlayerByName(playerName)
        assert isinstance(self.player, model.Player)

        self.gamePanel = GamePanel(self, self.game, self.player)
        #self.controller.model.subscribe(self.gamePanel, "msg_new_game", self.gamePanel.onMsgNewGame)
        self.controller.model.subscribe(self.gamePanel, "msg_game_loaded", self.gamePanel.onMsgGameLoaded)
        self.controller.model.subscribe(self.gamePanel, "msg_game_reverted", self.gamePanel.onMsgGameReverted)
        #self.controller.model.subscribe(self.gamePanel, "msg_new_player", self.gamePanel.onMsgNewPlayer)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(ButtonBar(self, self.controller, self.player))
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
        self.gameWindows = {}

        styles.init()

        iconFile = RESOURCES+"/yummy-icon-28-white.png"
        icon = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.gs = model.GameServer()
        self.gs.subscribe(self, "msg_new_game", self.onMsgNewGame)
        self.gs.subscribe(self, "msg_game_updated", self.onMsgGameUpdated)
        self.currentGame = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        #self.addTestTileWidgets()

        self.create_menu()
        self.SetSizer(self.sizer)
        #self.SetAutoLayout(1)
        #self.sizer.Fit(self)
        self.Centre()
        self.SetClientSize(400,300)
        self.Show()
        self.Bind(event=wx.EVT_CLOSE, handler=self.onUserCloseMainWindow)

    def addTestTileWidgets(self):
        '''
        REMOVE!!
        '''
        tc = model.TileContainer(None)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        for c in model.GameConstants.TILECOLORS:
            hbox.Add(TileWidget(self, model.Tile.create(200+c, c, 10, tc)))
        self.sizer.Add(hbox)

        
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

    def destroyGameWindows(self):
        for btn, w in self.gameWindows.items():
            btn.Destroy()
            w.Destroy()
        self.playerBtns = []
        
    def addPlayerButton(self, player): 
        assert isinstance(player, model.Player)   
        btnPlayer = wx.Button(self, -1, player.getName(), size=(100, 20), )
        gw = GameWindow(Controller(model.SynchronizingModel(self.gs, self.currentGame)), player.getName())
        gw.Bind(event=wx.EVT_CLOSE, handler=self.onUserCloseGameWindow)
        self.gameWindows[btnPlayer] = gw
        btnPlayer.Bind(wx.EVT_BUTTON, self.onUserPlayerClick)
        self.sizer.Add(btnPlayer)
        self.Refresh()

    def refresh(self):
        game = self.gs.getGame(self.currentGame)
        self.destroyGameWindows()
        for player in game.getPlayers():
            self.addPlayerButton(player)

    def onMsgNewGame(self, payload):
        pass

    def onMsgGameUpdated(self, payload):
        pass

    def onUserPlayerClick(self, e):
        gw = self.gameWindows[e.GetEventObject()]
        gw.Show()

    def onUserCloseMainWindow(self, e):
        for w in self.gameWindows.values():
            w.Destroy()
        e.Skip()

    def onUserCloseGameWindow(self, e):
        log.debug(function=self.onUserCloseGameWindow, args=e.GetEventObject().player.getName())
        if e.CanVeto():
            e.GetEventObject().Hide()
            e.Veto()

    def onUserExit(self, e):
        self.destroyGameWindows()
        self.Close(True) 

    def onUserNewGame(self, e):
        self.destroyGameWindows()
        self.currentGame = self.gs.newGame(2)
        self.gs.addPlayer(self.currentGame, "player1")
        self.gs.addPlayer(self.currentGame, "player2")
        self.gs.startGame(self.currentGame)
        self.refresh()

    def onUserSaveGame(self, e):
        if self.currentGame:
            # Create open file dialog
            dlg = wx.FileDialog(self, "Save", "", "", 
                "Yummy files (*.yummy)|*.yummy", 
                wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            path = dlg.GetPath()
            dlg.Destroy()

            self.gs.saveGame(self.currentGame, path)

    def onUserLoadGame(self, e):
        # Create open file dialog
        dlg = wx.FileDialog(self, "Open", "", "", 
            "Yummy files (*.yummy)|*.yummy", 
            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        path = dlg.GetPath()
        dlg.Destroy()
       
        self.currentGame = self.gs.loadGame(path)
        self.refresh()

    def onUserShowInspectionTool(self, e):
        wx.lib.inspection.InspectionTool().Show()


import logging

def start():
    logging.basicConfig(format='[%(name)s] %(levelname)s:%(message)s', level=logging.DEBUG)
    log.setLoggerLevel("persistentobject", logging.ERROR)
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
