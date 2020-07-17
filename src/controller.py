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

    def addPlayer(self, name):
        self.model.addPlayer(name)

    def getCurrentGame(self):
        return self.model.getCurrentGame()

    def getPlayer(self, name):
        return self.model.getPlayer(name)

