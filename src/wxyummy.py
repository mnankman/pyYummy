import asyncio

import wx
from wxasync import WxAsyncApp
from wx.lib.inspection import InspectionTool

from lib import log

from gui import styles
from gui.gamepanels import GamePanel

from base.model import Player, SynchronizingModel
from base.controller import Controller
from base import gameserver

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
        e.Skip()

    def onUserPlay(self, e):
        if self.checkPlayerTurn():
            self.controller.commit()
        else:
            self.controller.revert()
        self.controller.getCurrentGame().print()
        e.Skip()

    def onUserToggleSort(self, event):
        self.parent.onUserToggleSort(event)
        event.Skip()

class GameWindow(wx.Frame):
    def __init__(self, controller, playerName):
        super().__init__(parent=None, title=playerName)
        iconFile = RESOURCES+"/yummy-icon-28-white.png"
        icon = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        
        self.controller = controller

        self.game = self.controller.getCurrentGame()
        self.player = self.game.getPlayerByName(playerName)
        assert isinstance(self.player, Player)

        self.gamePanel = GamePanel(self, self.controller, self.player)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(ButtonBar(self, self.controller, self.player))
        self.sizer.Add(self.gamePanel, 1, wx.EXPAND)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Centre()


    def onUserToggleSort(self, e):
        self.gamePanel.toggleSort()
        e.Skip()

class GamePopupMenu(wx.Menu):

    def __init__(self, parent, gameNr):
        super(GamePopupMenu, self).__init__()

        self.parent = parent
        self.gameNr = gameNr

        pmi = wx.MenuItem(self, wx.NewId(), 'Play')
        self.Append(pmi)
        self.Bind(wx.EVT_MENU, self.OnPlay, pmi)

        smi = wx.MenuItem(self, wx.NewId(), 'Save')
        self.Append(smi)
        self.Bind(wx.EVT_MENU, self.OnSave, smi)


    def OnPlay(self, e):
        self.parent.play(self.gameNr)

    def OnSave(self, e):
        self.parent.save(self.gameNr)


class MainWindow(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Yummy', size=(500,100))
        self.gameWindows = {}

        styles.init()

        iconFile = RESOURCES+"/yummy-icon-28-white.png"
        icon = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.gs = gameserver.Factory()
        self.gs.subscribe(self, "msg_new_game", self.onMsgNewGame)
        self.gs.subscribe(self, "msg_game_updated", self.onMsgGameUpdated)
        self.gs.subscribe(self, "msg_game_loaded", self.onMsgGameLoaded)
        self.currentGame = None
        self.focusedGame = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.createMenu()
        self.createGameList()
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Centre()
        self.SetPosition((0, 0))
        self.SetSizer(self.sizer)
        self.Show()

        self.Bind(event=wx.EVT_CLOSE, handler=self.onUserCloseMainWindow)

        wx.PostEvent(self, wx.MenuEvent(wx.wxEVT_MENU, ID_NEWGAME))

    def createGameList(self):
        self.list = wx.ListCtrl(self, -1, style = wx.LC_REPORT|wx.LC_SORT_ASCENDING|wx.HSCROLL|wx.EXPAND) 
        self.list.InsertColumn(0, 'game', width = 50) 
        self.list.InsertColumn(1, 'players', wx.LIST_FORMAT_RIGHT, 100) 
        self.list.InsertColumn(2, 'moves', wx.LIST_FORMAT_RIGHT, 100) 
        self.list.InsertColumn(3, 'turn', wx.LIST_FORMAT_RIGHT, 100) 
        self.sizer.Add(self.list, 1, wx.EXPAND)

        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onUserGameListItemRightClick, self.list)

    def createMenu(self):
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
        for w in self.gameWindows.values():
            try:
                w.Destroy()
                del w
            finally:
                pass
        self.gameWindows = {}
        
    def play(self, gameNr):
        game = self.gs.getGame(gameNr)
        if gameNr == self.currentGame and len(self.gameWindows)>0:
            for player in game.getPlayers():
                nm = player.getName()
                self.gameWindows[nm].Show()
        else:
            self.destroyGameWindows()
            self.currentGame = gameNr
            for player in game.getPlayers():
                nm = player.getName()
                wPos = (len(self.gameWindows)*820, 200)
                c = Controller(SynchronizingModel(self.gs, self.currentGame))
                gw = GameWindow(c, player.getName())
                gw.SetPosition(wPos)
                gw.Bind(event=wx.EVT_CLOSE, handler=self.onUserCloseGameWindow)
                self.gameWindows[nm] = gw
                gw.Show()

    def save(self, gameNr):
        # Create open file dialog
        dlg = wx.FileDialog(self, "Save", "", "", 
            "Yummy files (*.yummy)|*.yummy", 
            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        path = dlg.GetPath()
        dlg.Destroy()
        self.gs.saveGame(gameNr, path)

        
    def refresh(self):
        pass

    def refreshList(self):
        self.list.DeleteAllItems()
        data = self.gs.getGameData()
        for row in data:
            index = self.list.InsertItem(5, str(row[0]))
            self.list.SetItem(index, 1, str(row[1])) 
            self.list.SetItem(index, 2, str(row[2]))
            self.list.SetItem(index, 3, str(row[3]))
            self.list.SetItemData(index, row[0])
        self.list.SortItems(lambda item1,item2: int(item1)-int(item2))
        if self.focusedGame==None:
            self.focusedGame = self.list.GetFocusedItem()
        elif self.focusedGame>=0:
            self.list.Focus(self.focusedGame)

    def onMsgNewGame(self, payload):
        self.refreshList()

    def onMsgGameUpdated(self, payload):
        self.refreshList()

    def onMsgGameLoaded(self, payload):
        self.refreshList()

    def onUserGameListItemRightClick(self, e):
        i = e.GetIndex()
        data = self.gs.getGameData()
        if data!=None and len(data)>0 and i>=0 :
            game = data[i][0]
            self.PopupMenu(GamePopupMenu(self, game), e.GetPoint())

    def onUserCloseMainWindow(self, e):
        for w in self.gameWindows.values():
            try:
                w.Destroy()
            finally:
                exit()
        e.Skip()

    def onUserCloseGameWindow(self, e):
        log.debug(function=self.onUserCloseGameWindow, args=e.GetEventObject().player.getName())
        if e.CanVeto():
            e.GetEventObject().Hide()
            e.Veto()

    def onUserExit(self, e):
        self.destroyGameWindows()
        self.Close(True) 
        e.Skip()

    def newGame(self):
        #self.destroyGameWindows()
        game = self.gs.newGame(2)
        self.gs.addPlayer(game, "player1")
        self.gs.addPlayer(game, "player2")
        self.gs.startGame(game)
        #self.refresh()

    def onUserNewGame(self, e):
        self.newGame()
        e.Skip()

    def onUserSaveGame(self, e):
        if self.currentGame:
            self.save(self.currentGame)
        e.Skip()

    def onUserLoadGame(self, e):
        # Create open file dialog
        dlg = wx.FileDialog(self, "Open", "", "", 
            "Yummy files (*.yummy)|*.yummy", 
            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        path = dlg.GetPath()
        dlg.Destroy()
        e.Skip()
       
        self.gs.loadGame(path)
        self.refresh()

    def onUserShowInspectionTool(self, e):
        InspectionTool().Show()
        e.Skip()


import logging

def start():
    logging.basicConfig(format='[%(name)s] %(levelname)s:%(message)s', level=logging.DEBUG)
    log.setLoggerLevel("base.persistentobject", logging.ERROR)
    log.setLoggerLevel("base.modelobject", logging.ERROR)
    log.setLoggerLevel("base.tilecontainer", logging.ERROR)
    log.setLoggerLevel("gui.tilewidgetview", logging.ERROR)
    log.setLoggerLevel("gui.tilesetwidget", logging.ERROR)
    log.setLoggerLevel("gui.gamepanels", logging.ERROR)
    app = WxAsyncApp()
    loop = asyncio.get_event_loop()
    w = MainWindow()
    try:
        loop.run_until_complete(app.MainLoop())
    finally:
        loop.stop()
        loop.close()

if __name__ == '__main__':
    start()
