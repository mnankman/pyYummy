from pubsub import Publisher
import random
import util

from log import Log
log = Log()
#log.setVerbosity(Log.VERBOSITY_VERBOSE)

class GameConstants:
    BLACK = 0
    BLUE = 1
    RED = 2
    ORANGE = 3
    NOCOLOR = 99
    TILECOLORS = [BLACK,BLUE,RED,ORANGE]
    TILECOLORNAMES = ["black", "blue", "red", "orange"]
    MAXTILEVALUE = 13
    TILEVALUES = range(1,MAXTILEVALUE+1)

class ModelObject(Publisher):
    EVENTS = ["msg_object_modified", "msg_new_child"]
    """
    This is the base class for all the other model classes. It implements the object 
    hierarchy and the model modification status. It extends Publisher to allow Subscriber 
    instances to be notified about the modification state.  
    """

    def __init__(self, parent=None):
        super().__init__(ModelObject.EVENTS)
        self.__modified__ = False
        self.__children__ = []
        self.__persistent__ = []
        self.__parent__ = None
        if parent:
            assert isinstance(parent, ModelObject)
            self.__parent__ = parent
            parent.addChild(self)

    def setModified(self):
        self.__modified__ = True
        self.dispatch("msg_object_modified", {"object": self} )

    def clearModified(self, recursive=False):
        self.__modified__ = False
        if recursive:
            for c in self.getChildren():
                c.clearModified(recursive)
        log.trace(type(self), ".clearModified(", recursive, ") --> ", self.__modified__)

    def getParent(self):
        return self.__parent__
    
    def isValidChild(self, child):
        valid = False
        if child and isinstance(child, ModelObject):
            valid = child in self.__children__ and child.getParent() == self
        return valid

    def getChildren(self):
        if not self.__children__: self.__children = []
        return self.__children__

    def addChild(self, childObject):
        assert isinstance(childObject, ModelObject)
        self.getChildren().append(childObject)
        assert self.isValidChild(childObject) == True
        self.dispatch("msg_new_child", {"object": self, "child": childObject})
        childObject.subscribe(self, "msg_object_modified", self.onMsgChildObjectModified)
        self.setModified()

    def onMsgChildObjectModified(self, payload):
        self.dispatch("msg_object_modified", {"object": self, "modified": payload})

    def isModified(self, recursive=False):
        if not self.__modified__ and recursive:
            return self.isChildModified(recursive)
        else:
            return self.__modified__

    def isChildModified(self, recursive=False):
        for c in self.getChildren():
            if recursive:
                return c.isModified(recursive)

    def getModifiedObjects(self):
        modified = []
        if self.__modified__:
            modified.append(self)
        for c in self.getChildren():
            modified = modified + c.getModifiedObjects()
        return modified

    def saveToDict(self):
        data = self.getData()
        for c in self.getChildren():
            childdata = c.saveToDict()
            if childdata and childdata["type"]:
                childtype = childdata["type"]
                if not "elements" in data:
                    data["elements"] = []
                data["elements"].append(childdata)
        return data

    def getType(self):
        """
        returns the type name for this ModelObject
        """
        return type(self).__name__
    
    def persist(self, persistentAttrName):
        self.__persistent__.append((type(self).__name__, persistentAttrName))
    
       
    def getPersistentAttributes(self):
        result = {}
        for pa in self.__persistent__:
            className = pa[0]
            attrName = pa[1]
            names = ["_"+className+"__"+attrName]
            for base in self.__class__.__bases__:
                names.append("_"+base.__name__+"__"+attrName)
            for nm in names:
                if nm in self.__dict__:
                    result[attrName] = self.__dict__[nm]
        log.trace("\n\n", type(self), ".getPersistentAttributes() -->", result, "\n\n")
        return result

    def getData(self, update=None):
        """
        must be overriden by subclasses
        it should return a dict with the following structure:
        {"type": "<type of the object>", "attr1": "<value of attr1>, ...}
        the type name is mandatory and is obtained by calling self.getType()
        through parameter "update", subclasses can add type specific data
        """
        data = {"type":self.getType()}
        data.update(self.getPersistentAttributes())
        if update: data.update(update)
        return data

    def isValidData(self, data):
        if data!=None and "type" in data and data["type"] == self.getType():
            log.trace(type(self),".isValidData(",data,")")
            return True
        return False

    def getDataType(self, data):
        if "type" in data: return data["type"]
        return None

    def getDataElements(self, data):
        if "elements" in data: return data["elements"]
        return None

    def getDataAttribute(self, data, attribute):
        if attribute in data: return data[attribute]
        return None
    
    def setDataAttributes(self, data):
        log.trace(type(self), ".setDataAttributes(", data, ")")
        className = self.getDataType(data)
        for item in data:
            if not item in ["type", "elements"]:
                attrValue = data[item]
                names = ["_"+className+"__"+item]
                for base in self.__class__.__bases__:
                    names.append("_"+base.__name__+"__"+item)
                for nm in names:
                    setterName = "set"+util.upperFirst(item)
                    if hasattr(type(self), setterName):
                        setter = getattr(type(self), setterName)
                        log.trace(setter, "(", attrValue, ")")
                        setter(self, attrValue)
                    else:
                        if hasattr(self, nm):
                            log.trace("set: ", nm, " = ", attrValue)
                            setattr(self, nm, attrValue)
                        else:
                            log.trace(className, "does not have an attribute named:" + item, 
                                "\n\n", type(self), ".__dict__", self.__dict__, "\n\n")
            
    def loadFromDict(self, data):
        log.trace("\n\n",type(self), ".loadFromDict(", data, ")")
        if self.isValidData(data):
            self.setDataAttributes(data)
            elements = self.getDataElements(data)
            if elements:
                for e in elements:
                    className = self.getDataType(data)
                    elementName = self.getDataType(e)
                    elementGetterName = "get"+self.getDataType(e)
                    elementAdderName = "add"+self.getDataType(e)
                    if hasattr(type(self), elementGetterName):
                        getElement = getattr(type(self), elementGetterName)
                        element = getElement(self)
                        assert isinstance(element, ModelObject)
                        element.loadFromDict(e)
                    elif hasattr(type(self), elementAdderName):
                        addElement = getattr(type(self), elementAdderName)
                        element = addElement(self)
                        assert isinstance(element, ModelObject)
                        element.loadFromDict(e)
                    else:
                        log.trace("no getter or creator method found for element", 
                                  className + "." + elementName, 
                                  "\n\n", type(self), ".__dict__", type(self).__dict__, "\n\n")



class Tile(ModelObject):
    __tiles__ = {}

    def create(id, color, value, container):
        if not id in __tiles__:
            tile = Tile(id, color, value, container)
            Tile.__tiles__[id] = tile
            return tile
        return None

    def add(tile):
        if not tile.id() in Tile.__tiles__: Tile.__tiles__[tile.id()] = tile

    def getById(id):
        return Tile.__tiles__[id]

    def __init__(self, id, color, value, container):
        super().__init__(None) # Tile instances have no parent for now
        self.__id = id
        self.__value = value
        self.__color = color
        self.persist("value")
        self.persist("color")
        self._container = container
        self.plate = None
        Tile.add(self)
        
    def getContainer(self):
        return self._container
    
    def setContainer(self, container):
        #log.trace(self.toString(), ".setContainer(", type(container), ")")
        self._container = container

    def id(self):
        return self.__id

    def move(self, targetContainer, pos=None):
        oldContainer = self._container
        if self._container.moveTile(self, targetContainer, pos):
            self.setModified()
            return True
        return False
        

    def rememberPlate(self, plate):
        if isinstance(plate, Plate):
            self.plate = plate
    
    def forgetPlate(self):
        self.plate = None

    def toString(self):
        s = "Tile" + str(self.__id) + "("
        s = s + str(self.__value) + ","
        s = s + GameConstants.TILECOLORNAMES[self.__color]
        s = s + ")"
        return s

    def getValue(self, *args, **kwargs):
        return self.__value

    def getColor(self, *args, **kwargs):
        return self.__color

    def print(self):
        log.trace(self.toString())

class Joker(Tile):
    def __init__(self, id, color, container):
        super().__init__(id, color, 0, container)

    def getNeighbours(self, *args, **kwargs):
        context = []
        try:
            context = kwargs["context"]
        except KeyError as e:
            if isinstance(self._container, Set): 
                context = self._container.getTilesAsDict()
        left,right = (None,None)
        if self in context:
            i = context.index(self)
            if i>0:
                left = context[i-1]
            if i<len(context)-1:
                right = context[i+1]
        """        
        log.trace(
            type(self), 
            ".getNeighbours(", 
            util.collectionToString(context, lambda item: item.toString() if item and isinstance(item, Tile) else str(item)), 
            ") --> ", 
            (left.toString() if left else None, right.toString() if right else None))
        """
        return (left,right)

    def getColor(self, *args, **kwargs):
        try:
            settype = kwargs["settype"]
        except KeyError as e:
            settype = None
        left,right = self.getNeighbours(*args, **kwargs)
        if left and right:
            if settype == Set.SETTYPE_RUN:
                return left.getColor()
            elif settype == Set.SETTYPE_GROUP:
                return GameConstants.NOCOLOR
        elif left:
            if settype == Set.SETTYPE_RUN:
                return left.getColor()
            elif settype == Set.SETTYPE_GROUP:
                return GameConstants.NOCOLOR
        elif right:
            if settype == Set.SETTYPE_RUN:
                return right.getColor()
            elif settype == Set.SETTYPE_GROUP:
                return GameConstants.NOCOLOR
        return super().getColor()

    def getValue(self, *args, **kwargs):
        try:
            settype = kwargs["settype"]
        except KeyError as e:
            settype = None
        left,right = self.getNeighbours(*args, **kwargs)
        if left and right:
            if settype == Set.SETTYPE_RUN:
                return left.getValue()+1
            elif settype == Set.SETTYPE_GROUP:
                return left.getValue()
        elif left:
            if settype == Set.SETTYPE_RUN:
                return left.getValue()+1
            elif settype == Set.SETTYPE_GROUP:
                return left.getValue()
        elif right:
            if settype == Set.SETTYPE_RUN:
                return right.getValue()-1
            elif settype == Set.SETTYPE_GROUP:
                return right.getValue()
        return super().getValue()

    def toString(self):
        s = "Joker(" + GameConstants.TILECOLORNAMES[self.getColor()] + ")"
        return s


class TileContainer(ModelObject):
    """
    Instances of this class can contain tiles. It implements the generic methods for this. 
    The specific container classes (such as Set, Board, Pile and Plate) extend this class.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.__tiles = []
        self.persist("tiles")
        self.lastTilePosition = 0

    def setTiles(self, tiles):
        if tiles:
            for tId in tiles:
                if not tId in self.__tiles:
                    tile = Tile.getById(tId)
                    if tile.getContainer() != self:
                        tile.move(self)
   
    def getTiles(self):
        return self.__tiles

    def getTilesAsDict(self):
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
        log.trace(type(self),".__removeTile(",tile.toString(),")")
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
        #log.trace(str(type(self)), ".addTile(", tile.toString(), ") --> ", fitPos)
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
        #log.trace(type(self), ".moveTile(", tile.toString(), targetContainer.toString(), ")")
        #log.trace("before move:", self.toString())
        tId = tile.id()
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

    def load(self, data):
        if self.isValidData(data):
            tiles = self.getDataAttribute(data, "tiles")
            if tiles:
                for tId in tiles:
                    tile = Tile.getById(tId)
                    tile.move(self)

    def toString(self):
        groupedByColor = sorted(self.getTilesAsDict().values(), key= lambda tile: tile.getColor())
        s = str(type(self)) + "(" + str(len(groupedByColor)) + " tiles):"
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
        self.persist("order")
        self.persist("pos")


    def load(self, data):
        super().load(data)
        if self.isValidData(data):
            self.__order = self.getDataAttribute(data, "order").copy()
            self.__pos = self.getDataAttribute(data, "pos")

    def getPos(self):
        return self.__pos
    
    def getOrder(self):
        return self.__order
    
    def setPos(self, pos):
        if (self.__pos == None) or pos[0] != self.__pos[0] or pos[1] != self.__pos[1]:
            self.__pos = pos
            self.setModified()
            log.trace(type(self), ".setPos", pos)

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
#            tile.forgetPlate()
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
                log.trace(type(self),".getOrderedTiles(): __tiles__ and order inconsistent")
                log.trace("__tiles__:", self.toString())
                log.trace("order:", self.__order)
                assert False
        log.trace(type(self),".getOrderedTiles() -->", 
            util.collectionToString(orderedTiles, lambda item: item.toString()))
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
        log.trace(type(self), ".isValidRun(", util.collectionToString(tiles, lambda item: str(item.getValue(context=tiles, settype = Set.SETTYPE_RUN))), ") --> ", (largestDiff,smallestDiff))
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
        containsjoker = jokers>0
        log.trace("N=",N,"DV=",DV,"DC=",DC,"jokers=",jokers)

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
            
        log.trace(
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
        self.persist("nextId")
        for color in GameConstants.TILECOLORS:
            for value in GameConstants.TILEVALUES:
                for i in range(2):
                    t = Tile(self.getNextId(), color, value, self)
                    TileContainer.addTile(self, t)
        TileContainer.addTile(self, Joker(self.getNextId(), GameConstants.BLACK, self))
        TileContainer.addTile(self, Joker(self.getNextId(), GameConstants.RED, self))

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
            #log.trace("pick: ", pick)
            pickedTile = self.getTile(pick)
            log.trace("picked: ", pickedTile.toString())
            pickedTile.move(player.plate)
        return pickedTile


class Board(TileContainer):
    def __init__(self, parent):
        super().__init__(parent)
        self.sets = []
        
    def addSet(self):
        set = Set(self)
        self.sets.append(set)
        return set
        
    def cleanUp(self, validateSets=True):
        log.trace(type(self),".cleanUp(validateSets=",validateSets,")")
        #cleanup unfinished and invalid sets
        for s in self.sets:
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
        for s in self.sets:
            if s.isEmpty():
                self.sets.pop(i)
            else:
                i+=1

    def addTile(self, tile, pos=None):
        TileContainer.addTile(self, tile, pos)
        set = self.addSet()
        tile.move(set)
        self.setModified()
        return 1

    def toString(self):
        s = "Board(" + str(len(self.sets)) + " sets):"
        for set in self.sets:
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

class Player(ModelObject):
    def __init__(self, game, name=None):
        super().__init__(game)
        self.plate = Plate(self)
        self.__name = name
        self.persist("name")
        self.game = game

    def getName(self):
        return self.__name
    
    def setName(self, name):
        self.__name = name

    def load(self, data):
        if self.isValidData(data):
            self.__name = self.getDataAttribute(data, "name")
            elements = self.getDataElements(data)
            if elements:
                for e in elements:
                    if self.getDataType(e) == "Plate": 
                        self.plate.load(e)

    def getPlate(self):
        return self.plate

    def pickTile(self):
        return self.game.pile.pickTile(self)

    def commitMoves(self):
        self.game.commitMoves(self)

    def toString(self):
        s =  "player: " + self.__name + self.plate.toString()
        return s

    def print(self):
        log.trace(self.toString())

class Game(ModelObject):
    def __init__(self, maxPlayers=4):
        super().__init__()
        self._players = []
        self.board = Board(self)
        self.pile = Pile(self)
        self.__maxPlayers = maxPlayers
        self.__currentPlayer = None
        self.persist("maxPlayers")
        self.persist("currentPlayer")
        
    def getBoard(self):
        return self.board
    
    def getPile(self):
        return self.pile

    def addPlayer(self):
        if len(self._players) < self.__maxPlayers:
            player = Player(self)
            self._players.append(player)
            self.setModified()
            return player

    def addPlayerByName(self, name):
        if not self.getPlayerByName(name):
            if len(self._players) < self.__maxPlayers:
                self._players.append(Player(self, name))
                self.setModified()

    def start(self, player):
        self.__currentPlayer = player.getName()
        for p in self._players:
            for i in range(14):
                p.pickTile()

    def getPlayerByName(self, name):
        player = None
        for p in self._players:
            if p.getName() == name:
                player = p
                break
        #log.trace(type(self), ".getPlayerByName(", name, ") --> ", player)
        return player

    def getCurrentPlayer(self):
        if self.__currentPlayer:
            return self.getPlayerByName(self.__currentPlayer)
        log.trace(type(self), ".getCurrentPlayer() --> None")
        return None

    def commitMoves(self, player):
        assert isinstance(player, Player)
        log.trace(type(self),".commitMoves(",player.getName(),")")
        if player.getName() == self.__currentPlayer and player.getParent() == self:
            # clean the board with validation
            self.board.cleanUp(True)
            # recursively clear the modified flag of all ModelObject instances under Game
            self.clearModified(True) 

    def toString(self):
        s = "\ngame(" + str(len(self._players)) + " players):\n"
        for p in self._players:
            s = s + p.toString()
        s = s + "\npile: " + self.pile.toString()
        s = s + "\nboard: " + self.board.toString()
        return s

    def print(self):
        log.trace(self.toString())


class Model(Publisher):
    EVENTS = ["msg_new_game", "msg_new_player", "msg_game_loaded"]
    def __init__(self):
        self.currentGame = None
        super().__init__(Model.EVENTS)

    def newGame(self, n):
        if self.currentGame:
            del self.currentGame
        self.currentGame = Game(n)
        self.dispatch("msg_new_game", {"game": self.currentGame})

    def start(self, player):
        self.currentGame.start(player)

    def loadGame(self, data):
        if self.currentGame:
            del self.currentGame
        self.currentGame = Game(0)
        self.currentGame.loadFromDict(data)
        self.dispatch("msg_game_loaded", {"game": self.currentGame})

    def addPlayer(self, name):
        if self.currentGame:
            self.currentGame.addPlayerByName(name)
            self.dispatch("msg_new_player", {"game": self.currentGame, "player": self.currentGame.getPlayerByName(name)})

    def getCurrentGame(self):
        return self.currentGame

    def isGameModified(self):
        return self.currentGame().isModified(True)

    def getPlayer(self, name):
        if self.currentGame:
            return self.currentGame.getPlayerByName(name)
        return None

    def getCurrentPlayer(self):
        return self.currentGame.getCurrentPlayer()




   