import wx
from wxasync import WxAsyncApp
import asyncio

import wx.lib.inspection

from tilewidget import TileWidget
from tilesetwidget import TileSetWidget
import dragable
import model
from controller import Controller
import util

from log import Log
log = Log()
log.setVerbosity(Log.VERBOSITY_VERBOSE)

RESOURCES="src/resource"

ID_NEWGAME=101
ID_SAVEGAME=102
ID_LOADGAME=103
ID_CONNECT=104
ID_EXIT=200
ID_SENDMESSAGE=500
ID_SHOWINSPECTIONTOOL=600

class ButtonPanel(wx.Panel):    
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



class BoardPanel(wx.Panel):    
    def __init__(self, parent):
        super().__init__(parent=parent, size=(800,500))
        self.parent = parent
        self.board = None
        self.SetBackgroundColour('#888888')
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_PAINT,self.onPaint)

    def getObjectsByType(self, type):
        result = []
        children = self.GetChildren()
        for c in children:
            if isinstance(c, type):
                result.append(c)
        return result

    def onPaint(self, event):
        event.Skip()
        tileSetWidgets = self.getObjectsByType(TileSetWidget)
        for tsw in tileSetWidgets:
            sx,sy,sw,sh = tsw.GetRect()
            xOffset = 3
            for t in tsw.set.getTilesSortedByValue():
                tw = self.parent.findTileWidgetById(t.id())
                if tw and not(tw.isBeingDragged()):
                    w,h = tw.GetSize()
                    tw.Move((sx+xOffset, sy+3))
                    tw.Raise()
                    tw.Refresh()
                    xOffset = xOffset + w 

    def reset(self, board):
        """
        destroys all instances of TileSetWidget that are currently being displayed        
        """
        assert isinstance(board, model.Board)
        for tileSetWidget in self.getObjectsByType(TileSetWidget):
            tileSetWidget.Destroy()
        self.board = board
        self.board.subscribe(self, "msg_new_child", self.onMsgBoardNewChild)

    def rebuild(self):
        """
        Rebuilds the visualisation of the sets (model.Set) that on the board (model.Board).
        First all instances of TileSetWidget are destroyed (by calling self.reset()).
        After that, a new TileSetWidget is created for each instance of model.Set on the board
        """
        self.reset(self.board)
        if self.board!=None:
            for set in self.board.sets:
                tileSetWidget = TileSetWidget(self, set)
                w,h = TileWidget.defaultSize()
                tileSetWidget.SetSize((w+6,h+10))
                tileSetWidget.setPos(set.pos)

    def cleanUpSets(self):
        for tileSetWidget in self.getObjectsByType(TileSetWidget):
            if tileSetWidget.set.isEmpty():
                tileSetWidget.Destroy()

    def findTileSetWidgetByOverlap(self, rect):
        children = self.GetChildren()
        result = None
        for tileSetWidget in self.getObjectsByType(TileSetWidget):
            if util.rectsOverlap(rect,tileSetWidget.GetRect()):
                result = tileSetWidget
                break
        return result

    def triggerTileSetWidgets(self, event):
        for tileSetWidget in self.getObjectsByType(TileSetWidget):
            tileSetWidget.onTileHover(event)

    def onTileHover(self, event):
        pos = event.pos
        self.triggerTileSetWidgets(event)

    def addTileSetWidget(self, set, pos=None):
        assert isinstance (set, model.Set)
        tileSetWidget = TileSetWidget(self, set)
        w,h = TileWidget.defaultSize()
        tileSetWidget.SetSize((w+6,h+10))
        tileSetWidget.setPos(pos if pos else set.pos)

    def onTileRelease(self, event):
        log.trace(type(self), ".onTileRelease(", event.pos, ",", event.obj.tile.toString())
        x,y = event.pos
        tile = event.obj.tile
        tileSetWidget = self.findTileSetWidgetByOverlap(event.obj.GetRect())
        if tileSetWidget:
            tileSetWidget.onTileRelease(event)
        else:
            log.trace ("released on board:", (x,y), event.obj.tile.toString())
            #move the tile to the board, this will result in a new instance of model.Set containing the tile:
            tile.move(self.board) 
            #tile.container is an instance of model.Set, set the position on the board:
            tile.container.setPos((x-3,y-4))
        event.obj.Raise()
        self.Refresh()

    def onMsgBoardNewChild(self, payload):
        log.trace(type(self),"received",payload)
        if payload["object"] == self.board and payload["child"] != None:
            self.addTileSetWidget(payload["child"])


class PlatePanel(wx.Panel):    
    def __init__(self, parent):
        super().__init__(parent=parent, size=(800,100))
        self.SetBackgroundColour('#CCCCCC')

class GamePanel(wx.Panel):    
    def __init__(self, parent):
        super().__init__(parent=parent, size=(800,600))
        self.SetBackgroundColour('#CCCCCC')
        self.__tileWidgets__ = None
        self.game = None
        self.sortMethod = 0
        
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.boardPanel = BoardPanel(self)
        self.platePanel = PlatePanel(self)
        vbox.Add(self.boardPanel, 1, wx.EXPAND)
        vbox.Add(self.platePanel, 1, wx.EXPAND)

        self.SetSizer(vbox)

    def getTileWidgets(self):
        return self.__tileWidgets__

    def addTileWidget(self, tileWidget):
        self.__tileWidgets__.append(tileWidget)

    def resetTileWidgets(self):
        if self.getTileWidgets() != None:
            for tileWidget in self.getTileWidgets():
                tileWidget.Destroy()
        self.__tileWidgets__ = []

    def getPlateValues(self):
        if self.game.getCurrentPlayer():
            plate = self.game.getCurrentPlayer().plate
            if self.sortMethod==0:
                return plate.getTiles().values()
            elif self.sortMethod==1:
                return plate.getTilesSortedByValue()
            else:
                return plate.getTilesGroupedByColor()

    def refreshTiles(self):
        if self.game.getCurrentPlayer():
            c = 0
            tx, ty = (0, 500)
            for t in self.getPlateValues():
                tileWidget = self.findTileWidgetById(t.id())
                if not tileWidget: 
                    tileWidget = TileWidget(self, t)
                    self.addTileWidget(tileWidget)
                    tileWidget.Bind(dragable.EVT_DRAGABLE_HOVER, self.boardPanel.onTileHover)
                    tileWidget.Bind(dragable.EVT_DRAGABLE_RELEASE, self.boardPanel.onTileRelease)
                tileWidget.Move((tx,ty))
                tw,th = tileWidget.GetSize()
                tx = tx+tw+1

    def findTileWidgetById(self, tId):
        for c in self.GetChildren():
            if isinstance(c, TileWidget):
                if tId==c.tile.id():
                    return c
        return None
            
    def reset(self, game):
        self.game = game
        self.boardPanel.reset(game.board)
        self.resetTileWidgets()
        self.refreshTiles()

    def getGame(self):
        return self.game

    def refresh(self):
        self.refreshTiles()
        self.boardPanel.cleanUpSets()
        self.Refresh()

    def toggleSort(self):
        if self.sortMethod<2:
            self.sortMethod+=1
        else:
            self.sortMethod = 0
        self.refreshTiles()
        self.Refresh()

class MainWindow(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Yummy')

        iconFile = RESOURCES+"/yummy-icon-28-white.png"
        icon = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.controller = Controller()
        self.controller.model.subscribe(self, "msg_new_game", self.onMsgNewGame)
        self.controller.model.subscribe(self, "msg_new_player", self.onMsgNewPlayer)
        self.controller.model.subscribe(self, "msg_game_loaded", self.onMsgGameLoaded)

        self.buttonPanel = ButtonPanel(self, self.controller)
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

    def onMsgNewGame(self, payload):
        log.trace(type(self),"received",payload)
        game = payload["game"]
        if game:
            game.subscribe(self, "msg_object_modified", self.onMsgGameModified)
            self.gamePanel.reset(game)

    def onMsgNewPlayer(self, payload):
        log.trace(type(self),"received",payload)
        player = payload["player"]
        if player:
            player.subscribe(self, "msg_object_modified", self.onMsgPlayerModified)
            self.controller.start(player)

    def onMsgGameLoaded(self, payload):
        log.trace(type(self),"received",payload)
        game = payload["game"]
        if game:
            game.subscribe(self, "msg_object_modified", self.onMsgGameModified)
            self.gamePanel.reset(game)

    def onMsgGameModified(self, payload):
        log.trace(type(self),"received",payload)
        self.gamePanel.refresh()

    def onMsgPlayerModified(self, payload):
        log.trace(type(self),"received",payload)
        self.gamePanel.refresh()

    def onUserExit(self, e):
        #answer = self.exitDialog.ShowModal()
        #if answer == wx.ID_YES:
        if True:
            self.Close(True) 

    def onUserNewGame(self, e):
        self.controller.newGame(2)
        self.controller.addPlayer("player1")

    def onUserSaveGame(self, e):
        self.controller.saveGame()

    def onUserLoadGame(self, e):
        self.controller.loadGame()

    def onUserShowInspectionTool(self, e):
        wx.lib.inspection.InspectionTool().Show()

    def onUserPlus(self, e):
        self.controller.pick()

    def onUserPlay(self, e):
        self.controller.commit()

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
