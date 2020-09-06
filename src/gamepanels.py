import wx
from tilewidget import TileWidget
from tilesetwidget import TileSetWidget
from tilewidgetview import TileWidgetView
from playerwidget import PlayerWidget
import draggable
import model
import util
import log

class BoardPanel(TileWidgetView):    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.board = None
        self.SetBackgroundColour('#888888')
        
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
            for tileWidget in self.getObjectsByType(TileWidget):
                tileWidget.Destroy()
            for set in self.board.getSets():
                tileSetWidget = TileSetWidget(self, set)
                tileSetWidget.setPos(set.getPos())
                tileSetWidget.rebuild()

    def cleanUp(self):
        for tileSetWidget in self.getObjectsByType(TileSetWidget):
            if tileSetWidget.set.isEmpty():
                tileSetWidget.Destroy()
            else:
                tileSetWidget.refreshLayout()
        for tileWidget in self.getObjectsByType(TileWidget):
            tileWidget.Destroy()

    def refresh(self):
        self.cleanUp()
        self.Refresh()

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

    def addTileSetWidget(self, set, pos=None):
        assert isinstance (set, model.Set)
        tileSetWidget = TileSetWidget(self, set)
        tileSetWidget.setPos(pos if pos else set.getPos())
        for tId in set.getOrder():
            tileWidget = self.findTileWidgetById(tId)
            if tileWidget and not(tileWidget.isBeingDragged()):
                tileWidget.Reparent(tileSetWidget)
        tileSetWidget.refreshLayout()
        tileSetWidget.Bind(draggable.EVT_DRAGGABLE_HOVER, self.onTileSetHover)
        tileSetWidget.Bind(draggable.EVT_DRAGGABLE_RELEASE, self.onTileSetRelease)

    def onTileSetHover(self, event):
        pos = event.pos
    
    def onTileSetRelease(self, event):
        log.debug(function=self.onTileSetRelease, args=event)
        tileSet = event.obj
        tileSet.accept(self)

    def onTileHover(self, event):
        log.debug(function=self.onTileHover, args=(event.pos, event.obj.tile))
        pos = event.pos
        self.triggerTileSetWidgets(event)

    def onTileRelease(self, event):
        log.debug(type(self), ".onTileRelease(", event.pos, ",", event.obj.tile.toString())
        x,y = self.getEventPosition(event)
        tx,ty,tw,th = self.getEventObjectRect(event)
        tile = event.obj.tile
        tileSetWidget = self.findTileSetWidgetByOverlap((x,y,tw,th))
        if tileSetWidget:
            tileSetWidget.onTileRelease(event)
        else:
            if (util.insideRect(event.obj.GetScreenRect(), self.GetScreenRect())):
                log.debug ("released on board:", (x,y), event.obj.tile.toString())
                event.obj.accept(self)
                #move the tile to the board, this will result in a new instance of model.Set containing the tile:
                tile.move(self.board) 
                #tile.container is an instance of model.Set, set the position on the board:
                tile.getContainer().setPos((x-3,y-4))
            else:
                event.obj.reject()
        self.Refresh()

    def onMsgBoardNewChild(self, payload):
        log.debug(type(self),"received",payload)
        if payload["object"] == self.board and payload["child"] != None:
            self.addTileSetWidget(payload["child"])

class PlatePanel(TileWidgetView):    
    def __init__(self, parent, player):
        super().__init__(parent)
        self.SetBackgroundColour('#CCCCCC')
        self.sortMethod = 0
        self.setPlayer(player)
        
    def setPlayer(self, player):
        if not player: return
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

    def reset(self):
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
        log.debug(function=self.onMsgPlayerModified, args=payload)
        self.refresh()

    def toggleSort(self):
        if self.sortMethod<2:
            self.sortMethod+=1
        else:
            self.sortMethod = 0
        self.refreshTiles()
        self.Refresh()

    def onTileRelease(self, event):
        log.debug(function=self.onTileRelease, args=(event.pos, event.obj.tile))
        tile = event.obj.tile
        if tile.plate == self.player.getPlate():
            event.obj.accept(self)
        else:
            event.obj.reject()


class GamePanel(TileWidgetView):    
    def __init__(self, parent, game, player):
        super().__init__(parent=parent, size=(800,600))
#        super().__init__(parent=parent)
        self.SetBackgroundColour('#CCCCCC')
        assert isinstance(game, model.Game)
        self.game = None
        self.sortMethod = 0
        
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.playerBox = wx.BoxSizer(wx.HORIZONTAL)
        for p in game.getPlayers():
            self.playerBox.Add(PlayerWidget(self, p))

        self.boardPanel = BoardPanel(self)
        self.platePanel = PlatePanel(self, player)
        self.platePanel.addTileWidgetDropTarget(self)
        self.boardPanel.addTileWidgetDropTarget(self)
        vbox.Add(self.boardPanel, 10, wx.EXPAND)
        vbox.Add(self.platePanel, 4, wx.EXPAND)
        vbox.Add(self.playerBox, 1, wx.EXPAND)

        self.SetSizer(vbox)

        self.reset(game)

    def reset(self, game):
        for tileSetWidget in self.getObjectsByType(TileSetWidget):
            tileSetWidget.Destroy()
        for tileWidget in self.getObjectsByType(TileWidget):
            tileWidget.Destroy()
        self.game = game
        self.game.subscribe(self, "msg_object_modified", self.onMsgGameModified)
        self.boardPanel.reset(game.board)
        self.platePanel.reset()

    def getGame(self):
        return self.game

    def refresh(self):
        self.platePanel.refresh()
        self.boardPanel.refresh()
        self.Refresh()

    def toggleSort(self):
        self.platePanel.toggleSort()

    def onMsgNewGame(self, payload):
        log.debug(function=self.onMsgNewGame, args=payload)
        game = payload["game"]
        if game:
            self.reset(game)
            
    def onMsgNewPlayer(self, payload):
        log.debug(function=self.onMsgNewPlayer, args=payload)
        player = payload["player"]
        if player:
            assert isinstance(player, model.Player)
            player.subscribe(self, "msg_object_modified", self.onMsgPlayerModified)
        pass

    def onMsgGameLoaded(self, payload):
        log.debug(function=self.onMsgGameLoaded, args=payload)
        game = payload["game"]
        if game:
            self.reset(game)
            self.refresh()

    def onMsgGameModified(self, payload):
        if not "modified" in payload: #only process modifications of game object, not of its children
            log.debug(function=self.onMsgGameModified, args=payload)
            self.refresh()

    def onMsgPlayerModified(self, payload):
#        if not "modified" in payload: #only process modifications of player object, not of its children
        if True:
            log.debug(function=self.onMsgPlayerModified, args=payload)
            player = payload["object"]
            if player:
                assert isinstance(player, model.Player)
                if self.game.getCurrentPlayer() == player:
                    self.refresh()

    def onTileRelease(self, event):
        log.debug(function=self.onTileRelease, args=(event.pos, event.obj.tile))
        if util.insideRect(event.pos, self.boardPanel.GetScreenRect()):
            self.boardPanel.onTileRelease(event)
        elif util.insideRect(event.pos, self.platePanel.GetScreenRect()):
            self.platePanel.onTileRelease(event)
        else:
            event.obj.reject()

    def onTileHover(self, event):
        if util.insideRect(event.pos, self.boardPanel.GetScreenRect()):
            self.boardPanel.onTileHover(event)
        elif util.insideRect(event.pos, self.platePanel.GetScreenRect()):
            self.platePanel.onTileHover(event)

