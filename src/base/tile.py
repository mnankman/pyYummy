from lib import log
from .modelobject import ModelObject
from . import model
from .gameconstants import GameConstants

class TileFactory:
    __instance__ = None
    
    def getInstance():
        if TileFactory.__instance__ == None: 
            TileFactory.init()
        return TileFactory.__instance__

    def init():
        if TileFactory.__instance__:
            del TileFactory.__instance__
        TileFactory.__instance__ = TileFactory.__TileFactory__()

    class __TileFactory__:

        def __init__(self):
            self.__tiles__ = {}

        def createTile(self, tId, color, value, container):
            if not tId in self.__tiles__:
                tile = Tile(tId, color, value, container, self)
                self.__tiles__[tId] = tile
                return tile
            return None

        def createJoker(self, tId, color, container):
            if not tId in self.__tiles__:
                tile = Joker(tId, color, container, self)
                self.__tiles__[tId] = tile
                return tile
            return None

        def add(self, tile):
            assert isinstance(tile, Tile)
            if not tile.id() in self.__tiles__: 
                self.__tiles__[tile.id()] = tile

        def getById(self, tId):
            return self.__tiles__[tId]

class Tile(ModelObject):

    def create(tId, color, value, container):
        return TileFactory.getInstance().createTile(tId, color, value, container)

    def getById(tId):
        return TileFactory.getInstance().getById(tId)

    def __init__(self, tId, color, value, container, factory):
        assert isinstance(factory, TileFactory.__TileFactory__)
        assert TileFactory.getInstance() == factory
        super().__init__(None) # Tile instances have no parent for now
        self.__id = tId
        self.__value = value
        self.__color = color
        self.persist("value")
        self.persist("color")
        self._container = container
        self.plate = None
        
    def getContainer(self):
        return self._container
    
    def setContainer(self, container):
        self._container = container

    def id(self):
        return self.__id

    def move(self, targetContainer, pos=None):
        if self._container.moveTile(self, targetContainer, pos):
            self.setModified()
            return True
        return False
        

    def rememberPlate(self, plate):
        if isinstance(plate, model.Plate):
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
    def create(tId, color, container):
        return TileFactory.getInstance().createJoker(tId, color, container)

    def __init__(self, id, color, container, factory):
        super().__init__(id, color, 0, container, factory)

    def getNeighbours(self, *args, **kwargs):
        context = []
        try:
            context = kwargs["context"]
        except KeyError:
            if isinstance(self._container, model.Set): 
                context = self._container.getTilesAsDict()
        left,right = (None,None)
        if self in context:
            i = context.index(self)
            if i>0:
                left = context[i-1]
            if i<len(context)-1:
                right = context[i+1]
        """        
        log.debug(
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
        except KeyError:
            settype = None
        left,right = self.getNeighbours(*args, **kwargs)
        if left and right:
            if settype == model.Set.SETTYPE_RUN:
                return left.getColor()
            elif settype == model.Set.SETTYPE_GROUP:
                return GameConstants.NOCOLOR
        elif left:
            if settype == model.Set.SETTYPE_RUN:
                return left.getColor()
            elif settype == model.Set.SETTYPE_GROUP:
                return GameConstants.NOCOLOR
        elif right:
            if settype == model.Set.SETTYPE_RUN:
                return right.getColor()
            elif settype == model.Set.SETTYPE_GROUP:
                return GameConstants.NOCOLOR
        return super().getColor()

    def getValue(self, *args, **kwargs):
        try:
            settype = kwargs["settype"]
        except KeyError:
            settype = None
        left,right = self.getNeighbours(*args, **kwargs)
        if left and right:
            if settype == model.Set.SETTYPE_RUN:
                return left.getValue()+1
            elif settype == model.Set.SETTYPE_GROUP:
                return left.getValue()
        elif left:
            if settype == model.Set.SETTYPE_RUN:
                return left.getValue()+1
            elif settype == model.Set.SETTYPE_GROUP:
                return left.getValue()
        elif right:
            if settype == model.Set.SETTYPE_RUN:
                return right.getValue()-1
            elif settype == model.Set.SETTYPE_GROUP:
                return right.getValue()
        return super().getValue()

    def toString(self):
        s = "Joker(" + GameConstants.TILECOLORNAMES[self.getColor()] + ")"
        return s

