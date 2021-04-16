from lib import log
from lib.pubsub import Publisher
import json
from . import model

class GameServer(Publisher):
    EVENTS = ["msg_new_game", "msg_game_updated", "msg_new_player"]
    def __init__(self):
        Publisher.__init__(self, GameServer.EVENTS)
        self.games = {}
        self.nextGameNr = 1

    def newGame(self, players):
        g = model.Game(players)
        gameNr = self.nextGameNr
        g.setGameNr(gameNr)
        self.games[gameNr] = g
        self.nextGameNr += 1
        self.dispatch("msg_new_game", {"id": self.games[gameNr].getId(), "game": self.games[gameNr].serialize()})
        return gameNr

    def getGame(self, gameNr):
        assert gameNr in self.games
        return self.games[gameNr].clone()

    def addPlayer(self, gameNr, name):
        g = self.getGame(gameNr)
        g.addPlayerByName(name)
        self.updateGame(g)
        del g

    def updateGame(self, game):
        gameNr = game.getGameNr()
        log.debug("--------------", function=self.updateGame, args=gameNr)
        self.games[gameNr] = game
        self.dispatch("msg_game_updated", {"id": game.getId(), "game": game.serialize(), "moves": game.getMoves()})

    def startGame(self, gameNr):
        assert gameNr in self.games
        log.debug(function=self.startGame, args=gameNr)
        self.games[gameNr].start()
        self.dispatch("msg_game_updated", {"id": self.games[gameNr].getId(), "game": self.games[gameNr].serialize(), "moves": self.games[gameNr].getMoves()})

    def saveGame(self, gameNr, path):
        assert gameNr in self.games
        log.debug(function=self.saveGame, args=gameNr)
        g = self.games[gameNr]
        self.saved = json.dumps(g.serialize())
        f=open(path,"w")
        f.write(self.saved)
        f.close()
        log.trace("game saved to:", path)

    def loadGame(self, path):
        log.debug(function=self.loadGame, args=path)
        f=open(path,"r")
        self.saved = f.readline()
        f.close()
        if self.saved:
            g = model.Game()
            g.deserialize(json.loads(self.saved))
            self.updateGame(g)
            #g.print()
            return g.getGameNr()
