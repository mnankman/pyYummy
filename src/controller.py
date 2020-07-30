from model import *

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

    def saveGame(self):
        self.saved = self.model.getCurrentGame().saveToDict()
        log.trace("game saved to:\n", self.saved)

    def loadGame(self):
        if self.saved:
            self.model.loadGame(self.saved)
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

