from pubsub import Publisher
from persistentobject import PersistentObject

from log import Log
log = Log()
#log.setVerbosity(Log.VERBOSITY_VERBOSE)

class ModelObject(PersistentObject, Publisher):
    EVENTS = ["msg_object_modified", "msg_new_child"]
    """
    This is the base class for all the other model classes. It implements the object 
    hierarchy and the model modification status. 
    extends PersistentObject to enable instance of ModelObject to serialize/deserialize their internal state
    extends Publisher to allow Subscriber instances to be notified about the modification state.  
    """

    def __init__(self, parent=None):
        PersistentObject.__init__(self)
        Publisher.__init__(self, ModelObject.EVENTS)
        self.__modified__ = False
        self.__children__ = []
        self.__parent__ = None
        if parent:
            assert isinstance(parent, ModelObject)
            self.__parent__ = parent
            parent.addChild(self)

    def __del__(self):
        #log.trace(type(self),".__del__()")
        for c in self.getChildren():
            del c

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

    def serialize(self):
        data = PersistentObject.serialize(self)
        for c in self.getChildren():
            childdata = c.serialize()
            data = self.addNestedElement(data, childdata)
        return data
