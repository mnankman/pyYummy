import wx
from gui.tilewidget import TileWidget
from gui.tilesetwidget import TileSetWidget
from gui.tilewidgetview import TileWidgetView
from gui.playerwidget import PlayerWidget
from gui import draggable
from base import model, controller
from lib import util, log

class BoardPanel(TileWidgetView):    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, name="board panel", *args, **kwargs)
        self.board = None
        self.SetBackgroundColour('#888888')
        
    def reset(self, board):
        """
        destroys all instances of TileSetWidget that are currently being displayed        
        """
        assert isinstance(board, model.Board)
        log.debug(function=self.reset, args=board)
        self.board = board
        #self.board.subscribe(self, "msg_new_child", self.onMsgBoardNewChild)
        self.board.subscribe(self, "msg_object_modified", self.onMsgBoardModified)
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

    def triggerTileSetWidgets(self, pos, widget):
        for tileSetWidget in self.getObjectsByType(TileSetWidget):
            if util.rectsOverlap(widget.GetScreenRect(), tileSetWidget.GetScreenRect()):
                tileSetWidget.onTileHover(pos, widget)

    def addTileSetWidget(self, set, pos=None):
        assert isinstance (set, model.Set)
        log.debug(function=self.addTileSetWidget, args=(set, pos))
        tileSetWidget = TileSetWidget(self, set)
        tileSetWidget.Bind(draggable.EVT_DRAGGABLE_HOVER, self.onTileSetHover)
        tileSetWidget.Bind(draggable.EVT_DRAGGABLE_RELEASE, self.onTileSetRelease)
        tileSetWidget.setPos(pos if pos else set.getPos())
        for tId in set.getOrder():
            tileWidget = self.findTileWidgetById(tId)
            if tileWidget and not(tileWidget.isBeingDragged()):
                tileWidget.Reparent(tileSetWidget)
        tileSetWidget.refreshLayout()

    def onTileSetRelease(self, pos, tileSetWidget):
        x,y = self.ScreenToClient(pos)
        log.debug(function=self.onTileSetRelease, args=((x,y), tileSetWidget))
        tileSetWidget.accept(self)
        tileSetWidget.setPos(pos)

    def onTileSetHover(self, pos, tileSetWidget):
        log.debug(function=self.onTileSetHover, args=event.pos)
        self.triggerTileSetWidgets(pos, tileSetWidget)

    def onTileHover(self, pos, tileWidget):
        #log.debug(function=self.onTileHover, args=(event.pos, event.obj.tile))
        self.triggerTileSetWidgets(pos, tileWidget)

    def onTileRelease(self, pos, tileWidget):
        log.debug(function=self.onTileRelease, args=(pos, tileWidget.GetName()))
        x,y = self.ScreenToClient(pos)
        tw,th = tileWidget.GetSize()
        tile = tileWidget.tile
        tileSetWidget = self.findTileSetWidgetByOverlap((x,y,tw,th))
        if tileSetWidget:
            tileSetWidget.onTileRelease(pos, tileWidget)
        else:
            if (util.insideRect(tileWidget.GetScreenRect(), self.GetScreenRect())):
                log.debug ("released on board:", (x,y), tile.toString())
                tileWidget.accept(self)
                #move the tile to the board, this will result in a new instance of model.Set containing the tile:
                tile.move(self.board) #this will add a new child (a new Set) to the board, and will be handled in onMsgBoardModified
                #tile.container is an instance of model.Set, set the position on the board:
                tile.getContainer().setPos((x-3,y-4))
            else:
                tileWidget.reject()
        self.Refresh()

    def onMsgBoardModified(self, payload):
        if not "modified" in payload: #only process modifications of board object, not of its children
            log.debug("*******", function=self.onMsgBoardModified, args=payload)
            self.rebuild()
            self.Refresh()

    """
    OBSOLETE?
    """
    def onMsgBoardNewChild(self, payload):
        log.debug(function=self.onMsgBoardNewChild)
        if payload["object"] == self.board and payload["child"] != None:
            self.addTileSetWidget(payload["child"])

class PlatePanel(TileWidgetView):    
    def __init__(self, parent, player, *args, **kwargs):
        super().__init__(parent, name="plate panel", *args, **kwargs)
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
        assert self.player!=None
        assert isinstance(self.player, model.Player)
        plate = self.player.plate
        result = None
        if self.sortMethod==0:
            result = plate.getTilesAsDict().values()
        elif self.sortMethod==1:
            result = plate.getTilesSortedByValue()
        else:
            result = plate.getTilesGroupedByColor()
        return result

    def reset(self, player=None):
        log.debug(function=self.reset, args=player)
        self.setPlayer(player)
        self.resetTileWidgets()
        self.refreshTiles()

    def refreshTiles(self):
        assert self.player!=None
        assert isinstance(self.player, model.Player)
        tx, ty = (0, 0)
        for t in self.getPlateValues():
            tileWidget = self.findTileWidgetById(t.id())
            if not tileWidget: 
                tileWidget = self.addTileWidget(t)
            tileWidget.Move((tx,ty))
            tw,th = tileWidget.GetSize()
            tx = tx+tw+1

    def refresh(self):
        self.refreshTiles()
        self.Refresh()

    def onMsgPlayerModified(self, payload):
        #log.debug(function=self.onMsgPlayerModified, args=payload)
        self.refresh()

    def toggleSort(self):
        if self.sortMethod<2:
            self.sortMethod+=1
        else:
            self.sortMethod = 0
        self.refreshTiles()
        self.Refresh()

    def onTileRelease(self, pos, tileWidget):
        log.debug(function=self.onTileRelease, args=(pos, tileWidget.tile))
        tile = tileWidget.tile
        if tile.plate == self.player.getPlate():
            tileWidget.accept(self)
        else:
            tileWidget.reject()


class GamePanel(wx.Panel):    
    def __init__(self, parent, cntrlr, player):
        super().__init__(parent=parent, name="game panel", size=(800,600), style=wx.TRANSPARENT_WINDOW)
#        super().__init__(parent=parent)
        #self.SetBackgroundColour('#CCCCCC')
        assert isinstance(cntrlr, controller.Controller)
        assert isinstance(player, model.Player)
        self.controller = cntrlr
        self.playerName = player.getName()
        self.sortMethod = 0
        
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.boardPanel = BoardPanel(self)
        self.platePanel = PlatePanel(self, self.getPlayer())
        self.playerBox = wx.BoxSizer(wx.HORIZONTAL)
        self.createPlayerWidgets()

        self.platePanel.addTileWidgetDropTarget(self.boardPanel)

        flexgrid = wx.FlexGridSizer(rows=3, cols=1, vgap=2, hgap=2)
        vbox.Add(flexgrid, 2, wx.EXPAND)
        flexgrid.Add(self.boardPanel, 0, wx.EXPAND)
        flexgrid.Add(self.platePanel)
        flexgrid.Add(self.playerBox)
        flexgrid.AddGrowableCol(0,1)
        flexgrid.AddGrowableRow(0,20)

        self.SetSizer(vbox)

        self.controller.model.subscribe(self, "msg_game_loaded", self.onMsgGameLoaded)
        self.controller.model.subscribe(self, "msg_game_reverted", self.onMsgGameReverted)

        self.reset()

    def __del__(self):
        self.controller.model.unsubscribe(self, self.onMsgGameLoaded, "msg_game_loaded")
        self.controller.model.unsubscribe(self, self.onMsgGameReverted, "msg_game_reverted")

    def getGame(self):
        assert controller!=None
        return self.controller.getCurrentGame()

    def getPlayer(self):
        return self.getGame().getPlayerByName(self.playerName)

    def reset(self):
        for c in self.GetChildren():
            if isinstance(c, PlayerWidget):
                player = self.getGame().getPlayerByName(c.player.getName())
                c.reset(player)
        self.getGame().subscribe(self, "msg_object_modified", self.onMsgGameModified)
        self.boardPanel.reset(self.getGame().board)
        self.platePanel.reset(self.getPlayer())

    def createPlayerWidgets(self):
        for p in self.getGame().getPlayers():
            self.playerBox.Add(PlayerWidget(self, p))

    def refresh(self):
        self.platePanel.refresh()
        if True or self.player().isPlayerTurn():
            self.boardPanel.refresh()            
        else:
            self.boardPanel.reset(self.getGame().board)
        self.Refresh()

    def toggleSort(self):
        self.platePanel.toggleSort()

    def onMsgGameLoaded(self, payload):
        log.debug(function=self.onMsgGameLoaded, args=payload)
        game = payload["game"]
        if game:
            self.reset()
            self.refresh()

    def onMsgGameReverted(self, payload):
        log.debug(function=self.onMsgGameLoaded, args=payload)
        game = payload["game"]
        if game:
            self.reset()
            self.refresh()

    def onMsgGameModified(self, payload):
        if not "modified" in payload: #only process modifications of game object, not of its children
            log.debug("*******", self.playerName, function=self.onMsgGameModified, args=payload)
            self.refresh()

    def onMsgPlayerModified(self, payload):
#        if not "modified" in payload: #only process modifications of player object, not of its children
        if True:
            log.debug(function=self.onMsgPlayerModified, args=payload)
            player = payload["object"]
            if player:
                assert isinstance(player, model.Player)
                if self.getGame().getCurrentPlayer() == player:
                    self.refresh()

