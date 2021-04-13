import util
from pubsub import Publisher
import log
import json
import model

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
        self.dispatch("msg_new_game", {"game": self.games[gameNr]})
        return gameNr

    def getGame(self, gameNr):
        assert gameNr in self.games
        return self.games[gameNr]

    def addPlayer(self, gameNr, name):
        g = self.getGame(gameNr)
        g.addPlayerByName(name)
        self.updateGame(g)
        del g

    def updateGame(self, game):
        gameNr = game.getGameNr()
        log.debug(function=self.updateGame, args=gameNr)
        self.games[gameNr] = game
        self.dispatch("msg_game_updated", {"game": self.games[gameNr]})

    def startGame(self, gameNr):
        log.debug(function=self.startGame, args=gameNr)
        self.getGame(gameNr).start()
        self.dispatch("msg_game_updated", {"game": self.games[gameNr]})

    def saveGame(self, gameNr, path):
        self.saved = json.dumps(self.gs.getGame(gameNr))
        f=open(path,"w")
        f.write(self.saved)
        f.close()
        log.trace("game saved to:", path)

    def loadGame(self, path):
        f=open(path,"r")
        self.saved = f.readline()
        f.close()
        if self.saved:
            g = model.Game(0)
            g.deserialize(json.loads(self.saved))
            self.updateGame(g)
            #g.print()
            return g.getGameNr()
