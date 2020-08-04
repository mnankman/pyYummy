import wx
from tilewidget import TileWidget
from tilesetwidget import TileSetWidget
import draggable
import model
import util

from log import Log
log = Log()

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
            for tId in tsw.set.order:
                tw = self.parent.findTileWidgetById(tId)
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
        self.board = board
        self.board.subscribe(self, "msg_new_child", self.onMsgBoardNewChild)
        self.rebuild()

    def rebuild(self):
        """
        Rebuilds the visualisation of the sets (model.Set) that on the board (model.Board).
        First all instances of TileSetWidget are destroyed.
        After that, a new TileSetWidget is created for each instance of model.Set on the board
        """
        if self.board!=None:
            for tileSetWidget in self.getObjectsByType(TileSetWidget):
                tileSetWidget.Destroy()
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
        self.__tileWidgets__ = []
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
                    tileWidget.Bind(draggable.EVT_DRAGGABLE_HOVER, self.boardPanel.onTileHover)
                    tileWidget.Bind(draggable.EVT_DRAGGABLE_RELEASE, self.boardPanel.onTileRelease)
                tileWidget.Move((tx,ty))
                tw,th = tileWidget.GetSize()
                tx = tx+tw+1
        for set in self.game.board.sets:
            sx, sy = set.pos 
            setTiles = set.order
            for tId in setTiles:
                tx, ty = (sx+2, sy+3)
                tileWidget = self.findTileWidgetById(tId)
                if not tileWidget: 
                    tileWidget = TileWidget(self, model.Tile.getById(tId))
                    self.addTileWidget(tileWidget)
                    tileWidget.Bind(draggable.EVT_DRAGGABLE_HOVER, self.boardPanel.onTileHover)
                    tileWidget.Bind(draggable.EVT_DRAGGABLE_RELEASE, self.boardPanel.onTileRelease)
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
        self.game.subscribe(self, "msg_object_modified", self.onMsgGameModified)
        if self.game.getCurrentPlayer():
            self.game.getCurrentPlayer().subscribe(self, "msg_object_modified", self.onMsgPlayerModified)
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

    def onMsgNewGame(self, payload):
        log.trace(type(self),"received",payload)
        game = payload["game"]
        if game:
            self.reset(game)
            
    def onMsgNewPlayer(self, payload):
        log.trace(type(self),"received",payload)
        player = payload["player"]
        if player:
            player.subscribe(self, "msg_object_modified", self.onMsgPlayerModified)
            self.refresh()

    def onMsgGameLoaded(self, payload):
        log.trace(type(self),"received",payload)
        game = payload["game"]
        if game:
            self.reset(game)

    def onMsgGameModified(self, payload):
        if not "modified" in payload: #only process modifications of game object, not of its children
            log.trace(type(self),"received",payload)
            self.refresh()

    def onMsgPlayerModified(self, payload):
        log.trace(type(self),"received",payload)
        self.refresh()

