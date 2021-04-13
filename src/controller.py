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
        log.debug(function=self.pick)
        self.model.pick()

    def commit(self):
        log.debug(function=self.commit)
        self.model.commitMoves()

    def revert(self):
        log.debug(function=self.revert)
        self.model.revertGame()

