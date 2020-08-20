import util

from log import Log
log = Log()
#log.setVerbosity(Log.VERBOSITY_VERBOSE)
    
class PersistentObject:
    """
    This class provides the methods necessary for persisting instance data and 
    serializing and deserializing of that data to a nested dictionary
    """
    def __init__(self):
        self.__persistent__ = []

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
        
    def getType(self):
        """
        returns the type name for this instance
        """
        return type(self).__name__
    
    def getData(self):
        """
        Returns a dict with the following structure:
        {"type": "<type of the object>", "attr1": "<value of attr1>, ...}
        """
        data = {"type":self.getType()}
        data.update(self.getPersistentAttributes())
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

    def addNestedElement(self, data, elementData):
        d = data.copy()
        if not "elements" in d:
            d["elements"] = []
        d["elements"].append(elementData)
        log.trace(type(self),".addNestedElement", (data, elementData), " --> ", d)
        return d

    def serialize(self):
        data = {"type":self.getType()}
        data.update(self.getPersistentAttributes())
        return data

    def deserialize(self, data):
        log.trace("\n\n",type(self), ".deserialize(", data, ")")
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
                        assert isinstance(element, PersistentObject)
                        element.deserialize(e)
                    elif hasattr(type(self), elementAdderName):
                        addElement = getattr(type(self), elementAdderName)
                        element = addElement(self)
                        assert isinstance(element, PersistentObject)
                        element.deserialize(e)
                    else:
                        log.trace("no getter or creator method found for element", 
                                  className + "." + elementName, 
                                  "\n\n", type(self), ".__dict__", type(self).__dict__, "\n\n")

