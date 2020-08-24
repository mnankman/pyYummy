import wx
from tilewidget import TileWidget
from tilesetwidget import TileSetWidget
import draggable
import model
import util

from log import Log
log = Log()

class TileWidgetViewListener:
    def onNewTileWidget(self, tileWidget):
        pass
    def onDestroyTileWIdget(self, tilewidget):
        pass

class TileWidgetView(wx.Panel):
    def __init__(self, listener=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__tileWidgets__ = []
        self.__listeners__ = []
        self.addListener(listener)
        
    def addListener(self, listener):
        if listener and isinstance(listener, TileWidgetViewListener):
            self.__listeners__.append(listener)
            
    def sendNewTileWidget(self, tw):
        assert isinstance(tw, TileWidget)
        for l in self.__listeners__:
            l.onNewTileWidget(tw)
            
    def sendDestroyTileWidget(self, tw):
        assert isinstance(tw, TileWidget)
        for l in self.__listeners__:
            l.onDestroyTileWidget(tw)

    def getTileWidgets(self):
        return self.__tileWidgets__

    def addTileWidget(self, tileWidget):
        self.__tileWidgets__.append(tileWidget)
        self.sendNewTileWidget(tileWidget)

    def findTileWidgetById(self, tId):
        for c in self.GetChildren():
            if isinstance(c, TileWidget):
                if tId==c.tile.id():
                    return c
        return None
 
    def resetTileWidgets(self):
        if self.getTileWidgets() != None:
            for tileWidget in self.getTileWidgets():
                tileWidget.Destroy()
        self.__tileWidgets__ = []


class BoardPanel(wx.Panel, TileWidgetViewListener):    
    def __init__(self, parent):
        #super().__init__(parent=parent, size=(800,500))
        super().__init__(parent=parent)
        self.parent = parent
        self.board = None
        self.SetBackgroundColour('#888888')
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_PAINT,self.onPaint)
        
    def onNewTileWidget(self, tw):
        tw.Bind(draggable.EVT_DRAGGABLE_HOVER, self.onTileHover)
        tw.Bind(draggable.EVT_DRAGGABLE_RELEASE, self.onTileRelease)

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
            for tId in tsw.set.getOrder():
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
            for set in self.board.getSets():
                tileSetWidget = TileSetWidget(self, set)
                w,h = TileWidget.defaultSize()
                tileSetWidget.SetSize((w+6,h+10))
                tileSetWidget.setPos(set.getPos())

    def cleanUpSets(self):
        for tileSetWidget in self.getObjectsByType(TileSetWidget):
            if tileSetWidget.set.isEmpty():
                tileSetWidget.Destroy()

    def findTileSetWidgetByOverlap(self, rect):
        result = None
        for tileSetWidget in self.getObjectsByType(TileSetWidget):
            if util.rectsOverlap(rect,tileSetWidget.GetRect()):
                result = tileSetWidget
                break
        log.debug("", function=self.findTileSetWidgetByOverlap, args=(rect,), returns=result)
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
        tileSetWidget.setPos(pos if pos else set.getPos())

    def onTileRelease(self, event):
        log.debug(type(self), ".onTileRelease(", event.pos, ",", event.obj.tile.toString())
        x,y = event.pos
        tx,ty,tw,th = event.obj.GetRect()
        tile = event.obj.tile
        tileSetWidget = self.findTileSetWidgetByOverlap((x,y,tw,th))
        if tileSetWidget:
            tileSetWidget.onTileRelease(event)
        else:
            log.debug ("released on board:", (x,y), event.obj.tile.toString())
            #move the tile to the board, this will result in a new instance of model.Set containing the tile:
            tile.move(self.board) 
            #tile.container is an instance of model.Set, set the position on the board:
            tile.getContainer().setPos((x-3,y-4))
        event.obj.Raise()
        #event.obj.Reparent(self)
        self.Refresh()

    def onMsgBoardNewChild(self, payload):
        log.debug(type(self),"received",payload)
        if payload["object"] == self.board and payload["child"] != None:
            self.addTileSetWidget(payload["child"])



class PlatePanel(TileWidgetView):    
    def __init__(self, parent):
#        super().__init__(parent=parent, size=(800,100))
        super().__init__(parent=parent)
        self.SetBackgroundColour('#CCCCCC')
        self.player = None
        self.sortMethod = 0
        
    def setPlayer(self, player):
        assert isinstance(player, model.Player)
        self.player = player
        self.player.subscribe(self, "msg_object_modified", self.onMsgPlayerModified)
        
    def getPlayer(self):
        if hasattr(self, "player"):
            return self.player
        return None

    def getPlateValues(self):
        if self.player and isinstance(self.player, model.Player):
            plate = self.player.plate
            if self.sortMethod==0:
                return plate.getTilesAsDict().values()
            elif self.sortMethod==1:
                return plate.getTilesSortedByValue()
            else:
                return plate.getTilesGroupedByColor()

    def reset(self, player):
        self.setPlayer(player)
        self.resetTileWidgets()
        self.refreshTiles()

    def refreshTiles(self):
        if self.player and isinstance(self.player, model.Player):
            c = 0
            tx, ty = (0, 0)
            for t in self.getPlateValues():
                tileWidget = self.findTileWidgetById(t.id())
                if not tileWidget: 
                    tileWidget = TileWidget(self, t)
                    self.addTileWidget(tileWidget)
                tileWidget.Move((tx,ty))
                tw,th = tileWidget.GetSize()
                tx = tx+tw+1

    def refresh(self):
        self.refreshTiles()
        self.Refresh()

    def onMsgPlayerModified(self, payload):
        log.debug(type(self),"received",payload)
        self.refresh()

    def onMsgNewPlayer(self, payload):
        log.debug(type(self),"received",payload)
        player = payload["player"]
        self.setPlayer(player)
        self.refresh()

    def toggleSort(self):
        if self.sortMethod<2:
            self.sortMethod+=1
        else:
            self.sortMethod = 0
        self.refreshTiles()
        self.Refresh()

class GamePanel(TileWidgetView):    
    def __init__(self, parent):
        super().__init__(parent=parent, size=(800,600))
#        super().__init__(parent=parent)
        self.SetBackgroundColour('#CCCCCC')
        self.game = None
        self.sortMethod = 0
        
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.boardPanel = BoardPanel(self)
        self.platePanel = PlatePanel(self)
        self.platePanel.addListener(self.boardPanel)
        vbox.Add(self.boardPanel, 5, wx.EXPAND)
        vbox.Add(self.platePanel, 2, wx.EXPAND)

        self.SetSizer(vbox)

    def refreshTiles(self):
        """
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
        """
        for set in self.game.board.getSets():
            sx, sy = set.getPos() 
            setTiles = set.getOrder()
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

    def reset(self, game):
        self.game = game
        self.game.subscribe(self, "msg_object_modified", self.onMsgGameModified)
        self.boardPanel.reset(game.board)
        self.resetTileWidgets()
        self.refreshTiles()

    def getGame(self):
        return self.game

    def refresh(self):
        #self.refreshTiles()
        self.platePanel.refresh()
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
        log.debug(type(self),"received",payload)
        game = payload["game"]
        if game:
            self.reset(game)
            
    def onMsgNewPlayer(self, payload):
        log.debug(type(self),"received",payload)
        player = payload["player"]
        self.platePanel.reset(player)

    def onMsgGameLoaded(self, payload):
        log.debug(type(self),"received",payload)
        game = payload["game"]
        if game:
            self.reset(game)

    def onMsgGameModified(self, payload):
        if not "modified" in payload: #only process modifications of game object, not of its children
            log.debug(type(self),"received",payload)
            self.refresh()

