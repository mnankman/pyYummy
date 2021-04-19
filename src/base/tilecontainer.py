import random
from lib import log, util
from lib.pubsub import Publisher
from .modelobject import ModelObject
from .gameserver import GameServer
from .gameconstants import GameConstants
from .tile import TileFactory, Tile, Joker

class TileContainer(ModelObject):
    """
    Instances of this class can contain tiles. It implements the generic methods for this. 
    The specific container classes (such as Set, Board, Pile and Plate) extend this class.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.__tiles = []
        self.persist("tiles", [])
        self.lastTilePosition = 0

    def setTiles(self, tiles):
        log.debug(function=self.setTiles, args=(self.getId(), tiles))
        if tiles:
            for tId in tiles:
                if not tId in self.__tiles:
                    tile = Tile.getById(tId)
                    if tile.getContainer() != self:
                        tile.move(self)
   
    def getTiles(self):
        return self.__tiles

    def getTilesAsDict(self):
        log.debug(function=self.getTilesAsDict, args=self.getId())
        tiles = {}
        for tId in self.__tiles:
            tiles[tId] = Tile.getById(tId)
        return tiles

    """
    Obsolete, but kept for compatibility
    """
    def copyTiles(self):
        return self.getTilesAsDict()

    def getSize(self):
        return len(self.__tiles)

    def getTile(self, tileId):
        tile = None
        if tileId in self.__tiles: 
            tile = Tile.getById(tileId)
        return tile

    def setTile(self, tile):
        tileId = tile.id()
        if not tileId in self.__tiles:
            self.__tiles.append(tileId)
        assert self.containsTile(tile)
        tile.setContainer(self)
        self.setModified()

    def containsTile(self, tile):
        """
        Parameters:
        - tileId: the id of a tile

        Returns: True if a tile with the provided id is contained within this Container,
        False otherwise
        """
        return tile.id() in self.__tiles
    
    def __removeTile(self, tile):
        #log.debug(function=self.__removeTile, args=tile.toString())
        tileId = tile.id()
        assert self.containsTile(tile)
        i = self.__tiles.index(tileId)
        self.__tiles.pop(i)
        assert self.containsTile(tile)==False
        

    def getTilesSortedByValue(self):
        return sorted(self.getTilesAsDict().values(), key= lambda tile: tile.getValue())

    def getTilesGroupedByColor(self):
        return sorted(self.getTilesSortedByValue(), key= lambda tile: tile.getColor())

    def addTile(self, tile, pos=None):
        """
        Parameters:
        - tile: an instance of class Tile
        Returns: the fit position of tile

        Adds a tile to this Container instance. The basic operation is to first determine
        the fit position for the new tile. If the tile does not fit (fitpos==0) the tile will 
        not be added to the container. 
        """
        fitPos = self.tileFitPosition(tile, pos)

        #log.debug(function=self.addTile, args=(tile.toString(),pos), returns=fitPos)

        if fitPos>0:
            self.setTile(tile)
            self.lastTilePosition = fitPos
        return fitPos

    def moveTile(self, tile, targetContainer, pos=None):
        """
        Parameters:
        - tile: an instance of class Tile
        - targetContainer: an instance of class Container

        Returns: True if the tile could be moved from this Container instance to targetContainer,
        False otherwise

        Moves the tile to the specified target container. In principal, this method should not be 
        invoked directly. To move a tile, invoke Tile.move().
        """
        if self.containsTile(tile):
            if targetContainer.addTile(tile, pos)>0:
                #self.__tiles.pop(self.__tiles.index(tId))
                self.__removeTile(tile)
                return True
        return False

    def findTile(self, value, color):
        for t in self.getTilesAsDict().values():
            if (t.getValue()==value and t.getColor()==color):
                return t

    def tileFitPosition(self, tile, pos=None):
        """
        Parameters:
        - tile: an instance of class Tile

        Returns: the position (by default: 1) where the new tile fits in this Container instance.
        
        The default operation for this base class is to always accept a Tile, so it simply returns 1.
        Extending classes may implement smarter methods for determining the fit position.
        """
        return 1

    def isEmpty(self):
        return (self.getSize()==0)

    def toString(self):
        groupedByColor = sorted(self.getTilesAsDict().values(), key= lambda tile: tile.getColor())
        s = self.getId() + "(" + str(len(groupedByColor)) + " tiles):"
        currentColor = None
        for tile in groupedByColor:
            if tile.getColor() != currentColor:
                currentColor = tile.getColor()
                s = s + "\n" + GameConstants.TILECOLORNAMES[currentColor] + ": "
            s = s + str(tile.getValue()) + " "
        return s

    def print(self):
        log.trace(self.toString())

class Set(TileContainer):
    """
    Instances of this class represent an ordered set of tiles on the board. 
    It provides the main methods for the game intelligence, such as the validation of a set, 
    and the functionality for determining whether a tile that a player drags into a set, fits or not. 
    """

    SETTYPE_UNDECIDED = 0   
    SETTYPE_GROUP = 1       #consists of tiles with different colors, but identical value
    SETTYPE_RUN = 2         #consists of tiles with different subsequent values of a single color
    SETTYPE_INVALID = -1
    SETTYPES = {
        SETTYPE_UNDECIDED: "Undecided",
        SETTYPE_GROUP: "Group",
        SETTYPE_RUN: "Run",
        SETTYPE_INVALID: "Invalid"
    }
    def __init__(self, parent, pos=None):
        super().__init__(parent)
        self.__order = []
        self.__pos = pos  #this is a tuple (x,y) and is the relative position of the set on the board
        self.persist("order", [])
        self.persist("pos")

    def getPos(self):
        return self.__pos
    
    def getOrder(self):
        return self.__order
    
    def setPos(self, pos):
        if (self.__pos == None) or pos[0] != self.__pos[0] or pos[1] != self.__pos[1]:
            self.__pos = pos
            self.setModified()
            log.debug(function=self.setPos, args=pos)

    def addTile(self, tile, pos=None):
        """
        Adds a tile to this Set instance. A set maintains the order in which tiles are added.
        Overrides Container.addTile(self, tile) to add logic ralated to the order of tiles.
        """
        fitPos = TileContainer.addTile(self, tile, pos)
        if pos==None and fitPos>0:
            if fitPos>len(self.__order):
                self.__order.append(tile.id())
            else:
                self.__order.insert(fitPos-1, tile.id())
        elif pos == fitPos:
            self.__order.insert(pos-1, tile.id())
            
        return fitPos

    def moveTile(self, tile, targetContainer, pos=None):
        """
        Moves tile from this Set to targetContainer. 
        Overrides TileContainer.moveTile(self, tile, targetContainer) to add logic related to 
        the order of tiles.
        """
        if super().moveTile(tile, targetContainer, pos):
            #tile.forgetPlate()
            i = self.__order.index(tile.id())
            self.__order.pop(i)
            return True
        return False

    def getOrderedTiles(self):
        orderedTiles = []
        for tId in self.__order:
            if tId in self.getTiles():
                orderedTiles.append(self.getTile(tId))
            else:
                log.error("__tiles__ and order inconsistent", function=self.getOrderedTiles)
                log.error("__tiles__:", self.toString())
                log.error("order:", self.__order)
                assert False
        log.debug(function=self.getOrderedTiles, returns=orderedTiles)
        return orderedTiles

    def isValidRun(self, tiles):
        """
        checks whether tiles is a valid run, by determining the largest and smallest difference between the tiles
        for a valid run, both the largest difference and smallest difference is exactly 1 
        """
        N = len(tiles)
        largestDiff = 0
        smallestDiff = GameConstants.MAXTILEVALUE
        for i in range(N):
            if i>0:
                prevValue = tiles[i-1].getValue(context = tiles, settype = Set.SETTYPE_RUN)
                thisValue = tiles[i].getValue(context = tiles, settype = Set.SETTYPE_RUN)
                diff = thisValue - prevValue
                if diff>largestDiff:
                    largestDiff = diff
                if diff<smallestDiff:
                    smallestDiff = diff
        log.debug(function=self.isValidRun, args=util.collectionToString(tiles, lambda item: str(item.getValue(context=tiles, settype = Set.SETTYPE_RUN))), returns=(largestDiff,smallestDiff))
        return (largestDiff==1 and smallestDiff==1)

    def getSetType(self, tiles):
        """
        Parameters:
        - tiles: a flat list of Tile instances (not a Dict)
        Returns: an int value representing the type of this set. Possible return values are:
        Set.SETTYPE_INVALID (-1) for an invalid set
        Set.SETTYPE_UNDECIDED (0) if the set type cannot be decided yet
        Set.SETTYPE_GROUP (1) if the set is a group (see below) 
        Set.SETTYPE_RUN (2) if the set is a run (see below) 

        Determines the type of the set, based on the current contents.
        A GROUP contains tiles of the same value, with different colors
        A RUN contains a number range (for example, 2,3,4) with the same color    
        """
        distinctcolors = {} 
        distinctvalues = {} 
        jokers=0
        for t in tiles:
            #get the value of the tile 
            #if t is an instance of Joker, than that value depends of its neighbours
            if isinstance(t,Joker):
                jokers+=1
            else:
                #count the distinct colors and values of the tiles (excluding jokers) in the set
                c = t.getColor(context = tiles)
                if c in distinctcolors: distinctcolors[c]+=1 
                else: distinctcolors[c]=1
                v = t.getValue(context = tiles)
                if v in distinctvalues: distinctvalues[v]+=1 
                else: distinctvalues[v]=1
        doublecolors = util.filteredCount(lambda x: x>1, distinctcolors.values())
        doublevalues = util.filteredCount(lambda x: x>1, distinctvalues.values())
        N = len(tiles)              #total number of tiles in the set
        DV = len(distinctvalues)    #number of distinct values in the set
        DC = len(distinctcolors)    #number of distinct colors in the set
        log.debug("N=",N,"DV=",DV,"DC=",DC,"jokers=",jokers)

        #the initial assumption is that the set is invalid
        settype = Set.SETTYPE_INVALID
        if (DC==1 and DV==1) or (N-jokers<=1):
            #the set contains a single tile or one or two jokers and one other tile, 
            #so the type cannot be determined yet
            settype = Set.SETTYPE_UNDECIDED
        elif DC==1 and DV>1:
            #multiple values of the same color, looks like a run 
            if doublevalues==0 and N<=13 and self.isValidRun(tiles):
                #now we are certain this is a valid run:
                settype = Set.SETTYPE_RUN
        elif DC>1 and DV==1:
            #multiple tiles with the same value but multiple colors, could be a group
            if doublecolors==0 and N<=4:
                #now we are certain this is a valid group
                settype = Set.SETTYPE_GROUP
            
        log.debug(
            type(self), 
            ".getSetType(", 
            util.collectionToString(
                tiles, 
                lambda item: str(item.getValue(context=tiles, settype=settype))), 
            ") --> ", 
            Set.SETTYPES[settype]
        )
        return settype

    def tileFitPosition(self, tile, pos=None):
        """
        Determines the fit position of tile in this Set
        Overrides Container.tileFitPosition(self, tile) to add logic related to 
        the order of tiles.
        """
        if self.containsTile(tile): return 0
        orderedTiles = self.getOrderedTiles()
        N = len(orderedTiles)
        if pos==None:
            #try adding the new tile at the end of the set
            if self.getSetType(orderedTiles+[tile]) != Set.SETTYPE_INVALID:
                return N+1
            #try adding the new tile at the beginning of the set
            elif self.getSetType([tile]+orderedTiles) != Set.SETTYPE_INVALID:
                return 1
            else:
                return 0
        elif pos>0:
            orderedTiles.insert(pos-1, tile)
            if self.getSetType(orderedTiles) != Set.SETTYPE_INVALID:
                return pos
            else:
                return 0

    def isValid(self):
        return self.getSize()>=3 and self.getSetType(self.getOrderedTiles()) != Set.SETTYPE_INVALID

class Pile(TileContainer):
    def __init__(self, parent):
        super().__init__(parent)
        self.__nextId = 0
        self.persist("nextId", 0)
        for color in GameConstants.TILECOLORS:
            for value in GameConstants.TILEVALUES:
                for i in range(2):
                    t = Tile.create(self.getNextId(), color, value, self)
                    TileContainer.addTile(self, t)
        TileContainer.addTile(self, Joker.create(self.getNextId(), GameConstants.BLACK, self))
        TileContainer.addTile(self, Joker.create(self.getNextId(), GameConstants.RED, self))

    def getNextId(self):
        nextId = self.__nextId
        self.__nextId = self.__nextId+1
        return nextId

    def pickTile(self, player):
        tiles = self.getTiles()
        n = len(tiles)
        pickedTile = None
        if n>0:
            pick = random.sample(list(tiles), 1)[0]
            #log.debug("pick: ", pick)
            pickedTile = self.getTile(pick)
            log.debug(function=self.pickTile, args=(player, pickedTile))
            pickedTile.move(player.plate)
        return pickedTile

class Board(TileContainer):
    def __init__(self, parent):
        super().__init__(parent)
        self.__sets = []
        
    def getSets(self):
        return self.__sets
        
    def addSet(self):
        set = Set(self)
        self.__sets.append(set)
        return set

    def validateSets(self):
        invalid = 0
        for s in self.__sets:
            if not s.isEmpty():
                if not s.isValid():
                    invalid += 1
        log.debug(function = self.validateSets, returns=invalid)
        return invalid

        
    def cleanUp(self, validateSets=True):
        log.debug(function=self.cleanUp, args=validateSets)
        #cleanup unfinished and invalid sets
        for s in self.__sets:
            if not s.isEmpty():
                if validateSets and s.isValid():
                    # make the valid moves permanent
                    for tId in s.copyTiles():
                        t = s.getTile(tId)
                        t.forgetPlate()
                else:
                    # undo the invalid moves (move back to the player's plate)
                    for tId in s.copyTiles():
                        t = s.getTile(tId)
                        if t.plate:
                            #move tile back to the current player's plate
                            t.move(t.plate)
        #remove all empty sets
        i = 0
        for s in self.__sets:
            if s.isEmpty():
                self.__sets.pop(i)
            else:
                i+=1

    def addTile(self, tile, pos=None):
        TileContainer.addTile(self, tile, pos)
        set = self.addSet()
        tile.move(set)
        self.setModified()
        return 1

    def toString(self):
        s = self.getId()+ "(" + str(len(self.__sets)) + " sets):"
        for set in self.__sets:
            s = s + "\n" + set.toString()
        return s

class Plate(TileContainer):
    def __init__(self, player):
        super().__init__(player)
        self.__player = player
        #self.persist("player")

    def getPlayer(self):
        return self.__player

    def moveTile(self, tile, targetContainer, pos=None):
        if TileContainer.moveTile(self, tile, targetContainer, pos):
            tile.rememberPlate(self)
            return True
        else:
            return False
