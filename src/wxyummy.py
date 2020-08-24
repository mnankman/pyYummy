import wx
from wxasync import WxAsyncApp
import asyncio

import wx.lib.inspection

from tilewidget import TileWidget
from tilesetwidget import TileSetWidget
from gamepanels import BoardPanel, GamePanel, PlatePanel
import draggable
import model
from controller import Controller
import util

from log import Log
log = Log()
log.setVerbosity(Log.VERBOSITY_DEBUG)

RESOURCES="src/resource"

ID_NEWGAME=101
ID_SAVEGAME=102
ID_LOADGAME=103
ID_CONNECT=104
ID_EXIT=200
ID_SENDMESSAGE=500
ID_SHOWINSPECTIONTOOL=600

class ButtonBar(wx.Panel):    
    def __init__(self, parent, controller):
        super().__init__(parent=parent, size=(800,45))
        self.parent = parent
        self.controller = controller

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

    def onUserPlus(self, e):
        self.controller.pick()

    def onUserPlay(self, e):
        self.controller.commit()
        self.controller.getCurrentGame().print()

    def onUserToggleSort(self, event):
        self.parent.onUserToggleSort(event)

class MainWindow(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Yummy')

        iconFile = RESOURCES+"/yummy-icon-28-white.png"
        icon = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.controller = Controller()
        self.controller.model.subscribe(self, "msg_new_player", self.onMsgNewPlayer)

        self.gamePanel = GamePanel(self)
        self.controller.model.subscribe(self.gamePanel, "msg_new_game", self.gamePanel.onMsgNewGame)
        self.controller.model.subscribe(self.gamePanel, "msg_game_loaded", self.gamePanel.onMsgGameLoaded)
        self.controller.model.subscribe(self.gamePanel, "msg_new_player", self.gamePanel.onMsgNewPlayer)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(ButtonBar(self, self.controller))
        self.sizer.Add(self.gamePanel, 1, wx.EXPAND)

        self.create_menu()
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Centre()
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
        log.debug(type(self),"received",payload)
        player = payload["player"]
        if player:
            self.controller.start(player)

    def onUserExit(self, e):
        #answer = self.exitDialog.ShowModal()
        #if answer == wx.ID_YES:
        if True:
            self.Close(True) 

    def onUserNewGame(self, e):
        self.controller.newGame(2)
        self.controller.addPlayer("player1")

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

    def onUserToggleSort(self, e):
        self.gamePanel.toggleSort()


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
