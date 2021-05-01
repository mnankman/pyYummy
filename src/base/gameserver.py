from lib import log
from lib.pubsub import Publisher
import json
from . import model
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer





class GameServer(Publisher):
    '''
    Abstract class that defines the interface of a GameServer
    '''
    EVENTS = ["msg_new_game", "msg_game_updated", "msg_game_loaded", "msg_new_player"]
    def __init__(self):
        Publisher.__init__(self, GameServer.EVENTS)

    def newGame(self, players):
        """
        Creates a new game with the indicated number of players. 
        Message "msg_new_game" will be dispatched so that listening subscribers can handle the update
        Parameters:
        - players: the number of players
        Returns: the number of the created game
        """
        pass

    def getGame(self, gameNr):
        """
        Returns a cloned version of the game indicated bij gameNr
        Parameters: 
        - gameNr: a number indicating the game that is to be returned
        Returns: an instance of model.Game
        """
        pass

    def getGameData(self):
        """
        Returns a list of data about the currently active games.
        Returns: an array of tuples (gameNr, number of players, move count, current player's name)
        """
        pass

    def addPlayer(self, gameNr, name):
        """
        Adds a new player to a game. It will cause an update to the game, which results in the 
        dispatch of message "msg_game_updated" so that listening subscribers can handle the update
        Parameters:
        - gameNr: the number of the game 
        - name: the name of the new player
        """
        pass

    def updateGame(self, game):
        """
        Updates a game. It will cause an update to the game, which results in the 
        dispatch of message "msg_game_updated" so that listening subscribers can handle the update
        Parameters:
        - game: an instance of model.Game
         """
        pass

    def startGame(self, gameNr):
        """
        Starts the game indicated by gameNr. Message "msg_game_updated" will be dispatched so that listening 
        subscribers can handle the update
        Parameters: 
        - gameNr: the number of the game
        """
        pass

    def saveGame(self, gameNr, path):
        """
        Saves a game in JSON-format to the indicated path. 
        Parameters:
        - gameNr: the number of the game that must be saved
        - path: the full pathname of the file that is created (or overwritten)
        """
        pass

    def loadGame(self, path):
        """
        Loads a game from a JSON-formatted file. After succesful loading, the game gets the next available game number.
        Message "msg_game_loaded" will be dispatched so that listening subscribers can handle the update
        Parameters:
        - path: the full pathname of the file that is created (or overwritten)
        """
        pass


class LocalGameServer(GameServer):
    '''
    This class implements a locally running GameServer instance. It can be built into 
    the UI of the game itself.
    '''
    def __init__(self):
        GameServer.__init__(self)
        self.__games__ = {} # a dictionary of model.Game instances, keyed by a unique gameNr
        self.__nextGameNr__ = 1

    def newGame(self, players):
        """
        Creates a new game with the indicated number of players. 
        Message "msg_new_game" will be dispatched so that listening subscribers can handle the update
        Parameters:
        - players: the number of players
        Returns: the number of the created game
        """
        g = model.Game(players)
        self._addGame(g)
        gameNr = g.getGameNr()
        self.dispatch("msg_new_game", {"id": self.__games__[gameNr].getId(), "gamenr": gameNr, "game": self.__games__[gameNr].serialize()})
        return gameNr

    def _addGame(self, game):
        """
        Adds the provided model.Game instance to the server, and gives it the next available number.
        Parameters:
        - game: the instance of model.Game
        """
        gameNr = self.__nextGameNr__
        game.setGameNr(gameNr)
        self.__games__[gameNr] = game
        self.__nextGameNr__ += 1

    def getGame(self, gameNr):
        """
        Returns a cloned version of the game indicated bij gameNr
        Parameters: 
        - gameNr: a number indicating the game that is to be returned
        Returns: an instance of model.Game
        """
        log.debug(function=self.getGame, args=gameNr)
        assert gameNr in self.__games__
        return self.__games__[gameNr].clone()

    def getGameData(self):
        """
        Returns a list of data about the currently active games.
        Returns: an array of tuples (gameNr, number of players, move count, current player's name)
        """
        result = []
        for gameNr,game in self.__games__.items():
            result.append((gameNr, game.getPlayerCount(), game.getMoves(), game.getCurrentPlayer().getName()))
        return result

    def addPlayer(self, gameNr, name):
        """
        Adds a new player to a game. It will cause an update to the game, which results in the 
        dispatch of message "msg_game_updated" so that listening subscribers can handle the update
        Parameters:
        - gameNr: the number of the game 
        - name: the name of the new player
        """
        g = self.getGame(gameNr)
        g.addPlayerByName(name)
        self.updateGame(g)
        del g

    def updateGame(self, game):
        """
        Updates a game. It will cause an update to the game, which results in the 
        dispatch of message "msg_game_updated" so that listening subscribers can handle the update
        Parameters:
        - game: an instance of model.Game
         """
        gameNr = game.getGameNr()
        log.debug("--------------", function=self.updateGame, args=gameNr)
        self.__games__[gameNr] = game
        self.dispatch("msg_game_updated", {"id": game.getId(), "gamenr": gameNr, "game": game.serialize(), "moves": game.getMoves()})

    def startGame(self, gameNr):
        """
        Starts the game indicated by gameNr. Message "msg_game_updated" will be dispatched so that listening 
        subscribers can handle the update
        Parameters: 
        - gameNr: the number of the game
        """
        assert gameNr in self.__games__
        log.debug(function=self.startGame, args=gameNr)
        self.__games__[gameNr].start()
        self.dispatch("msg_game_updated", {"id": self.__games__[gameNr].getId(), "gamenr": gameNr, "game": self.__games__[gameNr].serialize(), "moves": self.__games__[gameNr].getMoves()})

    def saveGame(self, gameNr, path):
        """
        Saves a game in JSON-format to the indicated path. 
        Parameters:
        - gameNr: the number of the game that must be saved
        - path: the full pathname of the file that is created (or overwritten)
        """
        assert gameNr in self.__games__
        log.debug(function=self.saveGame, args=gameNr)
        g = self.__games__[gameNr]
        saved = json.dumps(g.serialize())
        f=open(path,"w")
        f.write(saved)
        f.close()
        log.trace("game saved to:", path)

    def loadGame(self, path):
        """
        Loads a game from a JSON-formatted file. After succesful loading, the game gets the next available game number.
        Message "msg_game_loaded" will be dispatched so that listening subscribers can handle the update
        Parameters:
        - path: the full pathname of the file that is created (or overwritten)
        """
        log.debug(function=self.loadGame, args=path)
        f=open(path,"r")
        saved = f.readline()
        f.close()
        if saved:
            g = model.Game()
            data = json.loads(saved)
            g.deserialize(data)
            self._addGame(g)
            self.dispatch("msg_game_loaded", {"id": g.getId(), "gamenr": g.getGameNr(), "game": data})
            #g.print()
            return g.getGameNr()

def Factory(servertype="local"):
    '''
    A factory for instances of abstract class GameServer.
    Parameters:
    - servertype: a string representing the type of the required GameServer instance
    Returns: an instance of GameServer
    '''
    gameservers = {
        "local": LocalGameServer
    }
    assert servertype in gameservers
    return gameservers[servertype]()
