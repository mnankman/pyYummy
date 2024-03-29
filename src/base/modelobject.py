from lib import log
from lib.pubsub import Publisher
from .persistentobject import PersistentObject

class ModelObject(PersistentObject, Publisher):
    EVENTS = ["msg_object_modified", "msg_new_child"]
    """
    This is the base class for all the other model classes. It implements the object 
    hierarchy and the model modification status. 
    extends PersistentObject to enable instance of ModelObject to serialize/deserialize their internal state
    extends Publisher to allow Subscriber instances to be notified about the modification state.  
    """
    __lastId__ = 0
    def nextId():
        id = ModelObject.__lastId__
        ModelObject.__lastId__ += 1
        return id

    def __init__(self, parent=None):
        PersistentObject.__init__(self)
        Publisher.__init__(self, ModelObject.EVENTS)
        self.__modified__ = False
        self.__children__ = {}
        self.__parent__ = None
        self.__objectId__ = ModelObject.nextId()
        if parent:
            assert isinstance(parent, ModelObject)
            self.__parent__ = parent
            parent.addChild(self)

    def __del__(self):
        #log.trace(function=self.__del__, args=self.getFullId())
        self._reset()

    def _reset(self):
        for c in self.getChildren():
            del c
        self.__modified__ = False
        self.__children__ = {}

    def setModified(self):
        self.__modified__ = True
        self.dispatch("msg_object_modified", {"object": self} )

    def clearModified(self, recursive=False):
        self.__modified__ = False
        if recursive:
            for c in self.getChildren():
                c.clearModified(recursive)
        log.debug(type(self), ".clearModified(", recursive, ") --> ", self.__modified__)

    def getParent(self):
        return self.__parent__
    
    def isValidChild(self, child):
        valid = False
        if child and isinstance(child, ModelObject):
            valid = child in self.__children__.values() and child.getParent() == self
        return valid

    def getFullId(self):
        result = self.getId()
        p = self.getParent()
        if p!=None and isinstance(p, ModelObject):
            result = p.getFullId() + "/" + result
        return result

    def getId(self):
        return self.getType() + str(self.__objectId__)

    def getChildren(self):
        if not self.__children__: self.__children = []
        return self.__children__.values()

    def addChild(self, childObject):
        log.debug(function=self.addChild, args=childObject.getFullId())
        assert isinstance(childObject, ModelObject)
        self.__children__[childObject.getId()] = childObject
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

    def serialize(self):
        data = PersistentObject.serialize(self)
        for c in self.getChildren():
            childdata = c.serialize()
            data = self.addNestedElement(data, childdata)
        return data
