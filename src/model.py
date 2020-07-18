from pubsub import Publisher
import random

from log import Log
log = Log()
log.setVerbosity(Log.VERBOSITY_VERBOSE)

class ServerModel:
    def __init__(self):
        self.messages = []
        self.messageBoxes = {}

    def connectMessageBox(self, addr):
        self.messageBoxes[addr] = []
        for m in self.messages:
            self.messageBoxes[addr].append(m)

    def receiveMessage(self, m):
        self.messages.append(m)
        for addr in self.messageBoxes:
            self.messageBoxes[addr].append(m)

    def getAllMessages(self, addr):
        buf = b""
        for m in self.messageBoxes[addr]:
            buf += m
        return buf

    def clearMessages(self, addr):
        self.messageBoxes[addr] = []


# the events generated by a Model instance 
clientModelEvents = ["msg_received", "msg_sent"]

class ClientModel(Publisher):
    def __init__(self):
        self.received = []
        self.sent = []
        Publisher.__init__(self, clientModelEvents)

    def receiveMessage(self, m):
        self.received.append(m)
        Publisher.dispatch(self, "msg_received", (self.received, m))
 
    def addSentMessage(self, m):
        self.sent.append(m)
        Publisher.dispatch(self, "msg_sent", (self.sent, m))

class GameConstants:
    BLACK = 0
    BLUE = 1
    RED = 2
    ORANGE = 3
    TILECOLORS = [BLACK,BLUE,RED,ORANGE]
    TILECOLORNAMES = ["black", "blue", "red", "orange"]
    MAXTILEVALUE = 13
    TILEVALUES = range(1,MAXTILEVALUE+1)

class TileContainer:
    def __init__(self):
        self.tiles = {}
        self.lastTilePosition = 0

    def addTile(self, tile):
        fitPos = self.tileFitPosition(tile)
        log.trace(str(type(self)), ".addTile(", tile.toString(), ") --> ", fitPos)
        if fitPos>0:
            self.tiles[tile.id()] = tile
            self.lastTilePosition = fitPos
            tile.container = self
        return fitPos

    def moveTile(self, tile, targetContainer):
        #log.trace("moveTile(", tile.toString(), targetContainer.toString(), ")")
        #log.trace("before move:", self.toString())
        tId = tile.id()
        if tId in self.tiles:
            if targetContainer.addTile(tile)>0:
                self.tiles.pop(tId)
            return True
        else:
            return False

    def findTile(self, value, color):
        for t in self.tiles.values():
            if (t.value==value and t.color==color):
                return t

    def tileFitPosition(self, tile):
        return 1

    def isEmpty(self):
        return (len(self.tiles)==0)

    def toString(self):
        groupedByColor = sorted(self.tiles.values(), key= lambda tile: tile.color)
        s = str(type(self)) + "(" + str(len(groupedByColor)) + " tiles):"
        currentColor = None
        for tile in groupedByColor:
            if tile.color != currentColor:
                currentColor = tile.color
                s = s + "\n" + GameConstants.TILECOLORNAMES[currentColor] + ": "
            s = s + str(tile.getValue()) + " "
        return s

    def print(self):
        log.trace(self.toString())

class Game:
    def __init__(self, maxPlayers=4):
        self.players = {}
        self.board = Board()
        self.pile = Pile()
        self.maxPlayers = maxPlayers

    def addPlayer(self, name):
        if len(self.players) < self.maxPlayers:
            self.players[name] = Player(name, self)

    def getPlayer(self, name):
        return self.players[name]

    def toString(self):
        s = "\ngame(" + str(len(self.players)) + " players):\n"
        for name in self.players:
            s = s + self.players[name].toString()
        s = s + "\npile: " + self.pile.toString()
        s = s + "\nboard: " + self.board.toString()
        return s

    def print(self):
        log.trace(self.toString())


class Set(TileContainer):
    SETTYPE_COLORSET = 1
    SETTYPE_VALUESET = 2
    def __init__(self):
        TileContainer.__init__(self)
        self.order = []
        self.type = None

    def addTile(self, tile):
        fitPos = TileContainer.addTile(self, tile)
        if fitPos>0:
            if fitPos>len(self.order):
                self.order.append(tile.id())
            else:
                self.order.insert(fitPos-1, tile.id())
        return fitPos

    def isValid(self):
        """
        This method checks if the set is valid.
        All sets containing less than 3 tiles are invalid. 
        For sets containing >3 tiles it tries to determine the type of the set, based on the current contents.
        """
        valid = False
        if (len(self.tiles)>=3):
            colors = {} #dict for collecting all the colors in the set
            values = {} #dict for collecting all the values in the set
            for t in self.tiles.values():
                if not isinstance(t, Joker):
                    colors[t.color] = True
                    values[t.value] = True
            if len(colors)>=1 and len(values)==1:
                #the set contains multiple tiles with the same value, in multiple colors
                valid = True
            elif len(colors)==1 and len(values)>=1:
                #the set contains multiple values of a single color
                previousValue = None
                valid = True #assume the set is valid
                for tile in self.tiles.values():
                    #inspect the contents of the set to see if they are consequent
                    if previousValue==None:
                        previousValue = tile.value
                    else:
                        if isinstance(tile, Joker):
                            #a joker is always valid, skip it
                            previousValue+=1
                        else:
                            #the difference between consequent values should be 1
                            valid = (tile.value-previousValue == 1)
                            previousValue = tile.value
        return valid

    def tileFitPosition(self, tile):
        """
        This method checks if the new tile (tile) fits in this set.
        To do so it first tries to determine the type of the set, based on the current contents.
        A COLORSET contains tiles of the same value, with different colors
        A VALUESET contains a number range (for example, 2,3,4) with the same color    
        """
        colors = {} #dict for collecting all the colors in the set
        values = {} #dict for collecting all the values in the set
        for t in self.tiles.values():
            colors[t.color] = True
            values[t.value] = True
        values = sorted(values)
        settype = None
        if len(colors)==1 and len(values)==1:
            #the set contains a single tile
            if not(tile.color in colors) and (isinstance(tile, Joker) or tile.value in values):
                #the new tile is a joker, or the value of the new tile is contained in this set, but not its color
                settype = Set.SETTYPE_COLORSET
            elif not(isinstance(tile, Joker)) and not(tile.value in values):
                #the tile is not a joker and the value of the new tile is not contained in this set
                settype = Set.SETTYPE_VALUESET
        elif len(colors)>=1 and len(values)==1:
            #the set contains multiple tiles with the same value, in multiple colors
            if not(tile.color in colors) or isinstance(tile, Joker):
                #the set does not contain a tile with the new tile's color, or the new tile is a joker
                settype = Set.SETTYPE_COLORSET
        elif len(colors)==1 and len(values)>=1:
            #the set contains multiple values of a single color
            if not(tile.value in values):
                settype = Set.SETTYPE_VALUESET

        if settype==Set.SETTYPE_VALUESET:
            if isinstance(tile, Joker):
                return len(values)+1
            elif (values[0]==tile.value+1):
                return 1
            elif (values[len(values)-1]==tile.value-1):
                return len(values)+1
        elif settype==Set.SETTYPE_COLORSET:
            if len(colors)<4: 
                return len(colors)+1 
        elif len(values)==0:
            return 1
        
        #when arrived here we can assume that the tile does not fit, so return zero
        return 0

    def moveTile(self, tile, targetContainer):
        if TileContainer.moveTile(self, tile, targetContainer):
#            tile.forgetPlate()
            return True
        else:
            return False

class Tile:
    def __init__(self, id, color, value, container):
        self.__id__ = id
        self.value = value
        self.color = color
        self.container = container
        self.plate = None

    def id(self):
        return self.__id__

    def move(self, targetContainer):
        return self.container.moveTile(self, targetContainer)

    def rememberPlate(self, plate):
        if isinstance(plate, Plate):
            self.plate = plate
    
    def forgetPlate(self):
        self.plate = None

    def toString(self):
        s = "Tile" + str(self.__id__) + "("
        s = s + str(self.value) + ","
        s = s + GameConstants.TILECOLORNAMES[self.color]
        s = s + ")"
        return s

    def getValue(self):
        return self.value

    def print(self):
        log.trace(self.toString())

class Joker(Tile):
    def __init__(self, id, color, container):
        Tile.__init__(self, id, color, 0, container)

    def getValue(self):
        return ":-)"

    def toString(self):
        s = "Joker(" + GameConstants.TILECOLORNAMES[self.color] + ")"
        return s

class Pile(TileContainer):
    def __init__(self):
        self.nextId = 0
        TileContainer.__init__(self)
        for color in GameConstants.TILECOLORS:
            for value in GameConstants.TILEVALUES:
                for i in range(2):
                    t = Tile(self.getNextId(), color, value, self)
                    TileContainer.addTile(self, t)
        TileContainer.addTile(self, Joker(self.getNextId(), GameConstants.BLACK, self))
        TileContainer.addTile(self, Joker(self.getNextId(), GameConstants.RED, self))

    def getNextId(self):
        nextId = self.nextId
        self.nextId = self.nextId+1
        return nextId

    def pickTile(self, player):
        tiles = self.tiles.items()
        n = len(tiles)
        pickedTile = None
        if n>0:
            pickedTile = self.tiles[random.sample(list(self.tiles), 1)[0]]
            log.trace("picked: ", pickedTile.toString())
            pickedTile.move(player.plate)
        return pickedTile



class Board(TileContainer):
    def __init__(self):
        TileContainer.__init__(self)
        self.sets = []

    def createSet(self, tile):
        set = Set()
        tile.move(set)
        return set

    def cleanUp(self, validateSets=True):
        #cleanup unfinished and invalid sets
        for s in self.sets:
            if not s.isEmpty():
                if validateSets and s.isValid():
                    for tId in s.tiles.copy():
                        t = s.tiles[tId]
                        t.forgetPlate()
                else:
                    for tId in s.tiles.copy():
                        t = s.tiles[tId]
                        if t.plate:
                            #move tile back to the current player's plate
                            t.move(t.plate)
        #remove all empty sets
        i = 0
        for s in self.sets:
            if s.isEmpty():
                self.sets.pop(i)
            else:
                i+=1

    def addTile(self, tile):
        TileContainer.addTile(self, tile)
        set = self.createSet(tile)
        self.sets.append(set)
        return 1

    def toString(self):
        s = "Board(" + str(len(self.sets)) + " sets):"
        for set in self.sets:
            s = s + "\n" + set.toString()
        return s

class Plate(TileContainer):
    def __init__(self, player):
        self.player = player
        TileContainer.__init__(self)

    def moveTile(self, tile, targetContainer):
        if TileContainer.moveTile(self, tile, targetContainer):
            tile.rememberPlate(self)
            return True
        else:
            return False

class Player:
    def __init__(self, name, game):
        self.plate = Plate(self)
        self.name = name
        self.game = game
        for i in range(15):
            self.pickTile()

    def getPlate(self):
        return self.plate

    def pickTile(self):
        return self.game.pile.pickTile(self)

    def toString(self):
        s =  "player: " + self.name + self.plate.toString()
        return s

    def print(self):
        log.trace(self.toString())

class Model:
    def __init__(self):
        self.currentGame = None

    def newGame(self, n):
        self.currentGame = Game(n)

    def addPlayer(self, name):
        if self.currentGame:
            self.currentGame.addPlayer(name)

    def getCurrentGame(self):
        return self.currentGame

    def getPlayer(self, name):
        if self.currentGame:
            return self.currentGame.getPlayer(name)
        return None

class Test:
    def __init__(self):
        pass

    def runAllTests(self):
        self.runGameTest()
        self.runPlayerTest()

    def runGameTest(self):
        game = Game(4)
        game.log.trace()

        tc = game.board
        for v in range(1,4):
            t = game.pile.findTile(v, GameConstants.BLACK)
            t.log.trace()
            t.move(tc)
            tc = t.container
        game.log.trace()

    def runPlayerTest(self):
        game = Game(2)
        game.addPlayer("Joe")
        game.print()

        joe = game.getPlayer("Joe")
        joe.pickTile()
        joe.print()

        for tId in joe.plate.tiles:
            t = joe.plate.tiles[tId]
            log.trace("\nmoving to board:", t.toString())
            t.move(game.board)
            game.print()
            log.trace("\nboard.cleanUp:")
            game.board.cleanUp()
            game.print()
            log.trace("\nmoving back to plate:", t.toString())
            t.move(joe.plate)
            game.board.cleanUp()
            game.print()
            break

if __name__ == "__main__":
    test = Test()
    #test.runAllTests()
    test.runPlayerTest()

   