from model import *
import json

class Controller:
    def __init__(self):
        self.model = Model()

    def reset(self):
        self.model.init()

    def getModel(self):
        return self.model

    def newGame(self, n):
        self.model.newGame(n)

    def start(self, player):
        self.model.start(player)

    def saveGame(self, path):
        self.saved = json.dumps(self.model.getCurrentGame().saveToDict())
        f=open(path,"w")
        f.write(self.saved)
        f.close()
        log.trace("game saved to:", path)

    def loadGame(self, path):
        f=open(path,"r")
        self.saved = f.readline()
        f.close()
        if self.saved:
            self.model.loadGame(json.loads(self.saved))
            self.getCurrentGame().print()

    def addPlayer(self, name):
        self.model.addPlayer(name)

    def getCurrentGame(self):
        return self.model.getCurrentGame()

    def getCurrentPlayer(self):
        return self.model.getCurrentPlayer()

    def getPlayer(self, name):
        return self.model.getPlayer(name)

    def pick(self):
        player = self.getCurrentPlayer()
        if player:
            player.pickTile()
            self.getCurrentGame().board.cleanUp(False)

    def commit(self):
        player = self.getCurrentPlayer()
        if player:
            player.commitMoves()

