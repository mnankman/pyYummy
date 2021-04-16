import json
import random
from lib import log, util
from lib.pubsub import Publisher
from .modelobject import ModelObject
from .gameserver import GameServer
from .gameconstants import GameConstants
from .tile import TileFactory, Tile, Joker
from .tilecontainer import TileContainer, Set, Pile, Board, Plate

class Player(ModelObject):
    def __init__(self, game, name=None):
        super().__init__(game)
        self.plate = Plate(self)
        self.__name = name
        self.persist("name", None)
        self.game = game

    def getName(self):
        return self.__name
    
    def setName(self, name):
        self.__name = name
        self.setModified()

    def getPlate(self):
        return self.plate

    def isPlayerTurn(self):
        #log.debug(function=self.isPlayerTurn, args=self.__name)
        return self.game.getCurrentPlayer() == self

    def pickTile(self):
        return self.game.pile.pickTile(self)

    def toString(self):
        s =  "player: " + self.__name
        return s

    def print(self):
        log.trace(self.toString())

class Game(ModelObject):
    def __init__(self, maxPlayers=4):
        super().__init__()
        TileFactory.init() 
        self._players = []
        self.board = Board(self)
        self.pile = Pile(self)
        self.__maxPlayers = maxPlayers
        self.__currentPlayer = None
        self.__currentPlayerNr = None
        self.__gameNr = None
        self.__moves = 0
        self.persist("maxPlayers")
        self.persist("currentPlayer")
        self.persist("currentPlayerNr")
        self.persist("gameNr")
        self.persist("moves")
        
    def reset(self):
        TileFactory.init() 
        self._players = []
        self.board = Board(self)
        self.pile = Pile(self)
        
    def setCurrentPlayer(self, name):
        self.__currentPlayer = name
        self.setModified()
        
    def setCurrentPlayerNr(self, nr):
        log.debug(function=self.setCurrentPlayerNr, args=(self.getId(), nr))
        self.__currentPlayerNr = int(nr) if nr!=None else None
        self.setModified()
        
    def setMaxPlayers(self, maxPlayers):
        self.__maxPlayers = maxPlayers
        self.setModified()

    def setGameNr(self, gameNr):
        self.__gameNr = gameNr
        self.setModified()

    def setMoves(self, moves):
        self.__moves = moves
        self.setModified()

    def getGameNr(self):
        return self.__gameNr

    def getMoves(self):
        return self.__moves

    def incMoves(self):
        self.__moves += 1
        self.setModified()
        
    def getBoard(self):
        return self.board
    
    def getPile(self):
        return self.pile

    def addPlayer(self):
        log.debug(function=self.addPlayer, args=(self.getId(), len(self._players), self.__maxPlayers))
        if len(self._players) < self.__maxPlayers:
            player = Player(self)
            self._players.append(player)
            self.setModified()
            return player

    def addPlayerByName(self, name):
        if not self.getPlayerByName(name):
            if len(self._players) < self.__maxPlayers:
                self._players.append(Player(self, name))
                self.setModified()

    def start(self):
        log.trace(function=self.start)
        for p in self._players:
            for i in range(14):
                p.pickTile()
        self.__currentPlayerNr = 0
        self.__moves = 0

    def getPlayerByName(self, name):
        log.debug(function=self.getPlayerByName, args=(self.getId(), name, len(self._players)))
        player = None
        for p in self._players:
            if p.getName() == name:
                player = p
                break
        return player

    def getCurrentPlayer(self):
        cp = None
        #log.debug(function=self.getCurrentPlayer, args=(self.__currentPlayerNr, len(self._players)))
        if self.__currentPlayerNr!=None and self.__currentPlayerNr in range(len(self._players)):
            cp = self._players[self.__currentPlayerNr]
        if not cp: 
            log.error(function=self.getCurrentPlayer, returns=cp)
            assert False
        return cp

    def getPlayers(self):
        return self._players

    def nextTurn(self):
        p = self.__currentPlayerNr+1
        if p>=len(self._players): p = 0
        self.setCurrentPlayerNr(p)
        self.incMoves()
    
    def validate(self):
        return self.board.validateSets()==0
    
    def commit(self):
        # clean the board with validation
        self.board.cleanUp(True)
        # recursively clear the modified flag of all ModelObject instances under Game
        self.clearModified(True)
        self.nextTurn()

    def deserialize(self, data):
        self._players = []
        super().deserialize(data)

    def clone(self):
        log.debug(function=self.clone, args=self.getId())
        clonedGame = Game()
        data = self.serialize()
        clonedGame.deserialize(data)
        log.debug("\n\noriginal = " + str(data) + "\n\nclone = " + str(clonedGame.serialize()))
        return clonedGame

    def toString(self):
        s = "\n" + self.getId() + "(" + str(len(self._players)) + " players):\n"
        for p in self._players:
            s = s + p.toString() + p.plate.toString()
        s = s + "\npile: " + self.pile.toString()
        s = s + "\nboard: " + self.board.toString()
        return s

    def print(self):
        log.trace(self.toString())

class AbstractModel():
    def __init__(self):
        pass
    
    def rememberState(self, data=None):
        pass

    def newGame(self, n):
        pass

    def start(self):
        pass

    def pick(self):
        pass

    def commitMoves(self):
        pass

    def revertGame(self):
        pass

    def loadGame(self, data):
        pass

    def addPlayer(self, name):
        pass

    def getCurrentGame(self):
        pass
 
    def isGameModified(self):
        pass

    def getPlayer(self, name):
        pass

    def getCurrentPlayer(self):
        pass

class Model(AbstractModel, Publisher):
    EVENTS = ["msg_new_game", "msg_new_player", "msg_game_loaded", "msg_game_reverted", "msg_game_committed"]
    def __init__(self):
        self.currentGame = None
        self.lastValidState = None
        Publisher.__init__(self, Model.EVENTS)

    def rememberState(self, data=None):
        if not data: 
            data = self.currentGame.serialize()
        self.lastValidState = data
        log.trace("lastValidState =", self.lastValidState, function=self.rememberState)

    def newGame(self, n):
        log.trace(function=self.newGame, args=n)
        if self.currentGame:
            del self.currentGame
        self.currentGame = Game(n)
        self.dispatch("msg_new_game", {"game": self.currentGame})

    def start(self):
        self.currentGame.start()
        self.rememberState()

    def pick(self):
        log.debug(function=self.pick)
        player = self.getCurrentPlayer()
        game = self.getCurrentGame()
        if game and player:
            game.getPile().pickTile(player)
            game.board.cleanUp(False)
            game.nextTurn()

    def commitMoves(self):
        log.trace(function=self.commitMoves)
        if not self.getCurrentGame().validate():
            log.trace("There are invalid sets on the board, revert to last valid state")
            self.revertGame()
        else:
            self.getCurrentGame().commit()
            self.rememberState()

    def commitGame(self, serializedGame):
        log.trace(function=self.commitGame, args=serializedGame)
        if self.currentGame:
            del self.currentGame
        self.currentGame = Game(0)
        self.currentGame.deserialize(serializedGame)
        self.rememberState(serializedGame)
        self.dispatch("msg_game_committed", {"game": self.currentGame})

    def revertGame(self):
        if self.lastValidState:
            log.trace(function=self.revertGame)
            if self.currentGame:
                del self.currentGame
            self.currentGame = Game(0)
            self.currentGame.deserialize(self.lastValidState)
            self.dispatch("msg_game_reverted", {"game": self.currentGame})

    def loadGame(self, data):
        log.trace(function=self.loadGame)
        log.debug(function=self.loadGame, args=data)
        if self.currentGame == None:
            self.currentGame = Game()
        self.currentGame.deserialize(data)
        self.rememberState(data)
        self.dispatch("msg_game_loaded", {"game": self.currentGame})

    def addPlayer(self, name):
        log.trace(function=self.addPlayer, args=name)
        if self.currentGame:
            self.currentGame.addPlayerByName(name)
            self.dispatch("msg_new_player", {"game": self.currentGame, "player": self.currentGame.getPlayerByName(name)})

    def getCurrentGame(self):
        return self.currentGame

    def isGameModified(self):
        return self.currentGame().isModified(True)

    def getPlayer(self, name):
        if self.currentGame:
            return self.currentGame.getPlayerByName(name)
        return None

    def getCurrentPlayer(self):
        return self.currentGame.getCurrentPlayer()

class SynchronizingModel(Model):
    def __init__(self, gameserver, gameNr):
        Model.__init__(self)
        assert isinstance(gameserver, GameServer)
        self.gs = gameserver
        self.currentGame = self.gs.getGame(gameNr)
        self.gs.subscribe(self, "msg_new_game", self.onMsgNewGame)
        self.gs.subscribe(self, "msg_game_updated", self.onMsgGameUpdated)
    
    def start(self):
        pass

    def newGame(self, n):
        pass

    def pick(self):
        super().pick()
        self.gs.updateGame(self.getCurrentGame())

    def commitMoves(self):
        super().commitMoves()
        self.gs.updateGame(self.getCurrentGame())

    def addPlayer(self, name):
        super().addPlayer(name)
        self.gs.updateGame(self.getCurrentGame())
 
    def onMsgNewGame(self, payload):
        log.debug(function=self.onMsgNewGame)
        self.loadGame(payload["game"])

    def onMsgGameUpdated(self, payload):
        log.debug(function=self.onMsgGameUpdated, args=(self.getCurrentGame().getId(), self.getCurrentGame().getMoves(), payload["moves"]))
        if self.getCurrentGame().getMoves() < payload["moves"]:
            log.debug("a player has made a move, game of this model needs to be updated")
            self.loadGame(payload["game"])


