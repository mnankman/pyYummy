from model import *
import log
import json

class Controller:
    def __init__(self, model):
        assert model
        assert isinstance(model, AbstractModel)
        self.model = model

    def reset(self):
        self.model.init()

    def getModel(self):
        return self.model

    def newGame(self, n):
        self.model.newGame(n)

    def start(self):
        self.model.start()

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
        game = self.getCurrentGame()
        if game and player:
            game.getPile().pickTile(player)
            game.board.cleanUp(False)
            game.nextTurn()

    def commit(self):
        self.model.commitMoves()

    def revert(self):
        self.model.revertGame()

