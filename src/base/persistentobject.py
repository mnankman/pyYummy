from lib import log, util
   
class PersistentObject:
    """
    This class provides the methods necessary for persisting instance data and 
    serializing and deserializing of that data to a nested dictionary
    """
    def __init__(self):
        """
        Constructs an instance of PersistentObject. 
        __persistent__ contains all attributes marked as persistent. 
        It containts tuples of the format (classname, attribute name, initial value)
        """
        self.__persistent__ = [] 

    def persist(self, persistentAttrName, initValue=None):
        """
        marks the instance attribute indicated by persistentAttrName (str) as persistent
        initValue is None by default, but can be set to a specific value. 
        """
        self.__persistent__.append((type(self).__name__, persistentAttrName, initValue))
        
    def initPersistentAttributes(self):
        """
        initializes the persistent instance attributes 
        """
        for pa in self.__persistent__:
            className, attrName, initValue = pa
            names = ["_"+className+"__"+attrName]
            for base in self.__class__.__bases__:
                names.append("_"+base.__name__+"__"+attrName)
            for nm in names:
                if nm in self.__dict__:
                    setattr(self, nm, initValue)     
    
    def getPersistentAttributes(self):
        """
        returns a dictionary of the persistent attributes with their current values, 
        very much like the builtin method __dict__. 
        The format of the resulting dictionary is:
        {class.attr1: value1, class.attr2: value2, ...}
        """
        result = {} 
        for pa in self.__persistent__:
            className, attrName, initValue = pa
            names = ["_"+className+"__"+attrName]
            # construct a list of possible qualified names (class.attribute) for the attributes
            for base in self.__class__.__bases__:
                names.append("_"+base.__name__+"__"+attrName)
            # try each of these names
            for nm in names:
                # by looking it up in self.__dict__
                if nm in self.__dict__:
                    v = self.__dict__[nm]
                    # put (a copy of) the found value in result
                    result[attrName] = v.copy() if hasattr(type(v), "copy") else v
                    # if the value is a list, dict, etc, than store a copy of it
        #log.trace("\n\n", type(self), ".getPersistentAttributes() -->", result, "\n\n")
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
        """
        Checks the validity of the provided serialized data
        """
        log.debug(function=self.isValidData, args=(data, self.getType()))
        assert data!=None
        assert isinstance(data, dict)
        assert "type" in data
        assert data["type"] == self.getType()
        if data!=None and isinstance(data, dict) and "type" in data and data["type"] == self.getType():
            # valid data is a dict containing at least a field "type" with value self.classname
            return True
        log.error(function=self.isValidData, args=data, returns=False)
        # perhaps, we should raise an exception here, for now, False is returned
        return False

    def getDataType(self, data):
        """
        returns the type of the provided serialized data
        """
        if "type" in data: return data["type"]
        return None

    def getDataElements(self, data):
        """
        returns the list of elements in the provided serialized data
        """
        if "elements" in data: return data["elements"]
        return None

    def getDataAttribute(self, data, attribute):
        """
        returns the value of the provided attribute as serialized in data
        returns None if the attribute does not exist
        """
        if attribute in data: return data[attribute]
        return None
    
    def setDataAttributes(self, data):
        """
        sets the persistent attributes to the values as serialized in data 
        """
        log.debug(function=self.setDataAttributes, args=self.getType())
        className = self.getDataType(data)
        # iterate through the items in data
        for item in data:
            # skip the value of "type" and "elements" (which contains serialized data for child objects)
            if not item in ["type", "elements"]:
                attrValue = data[item]
                names = ["_"+className+"__"+item]
                # construct a list of possible qualified names (class.attribute)
                for base in self.__class__.__bases__:
                    names.append("_"+base.__name__+"__"+item)
                # try each of these names
                for nm in names:
                    # see if the class has a setter method for this attribute
                    setterName = "set"+util.upperFirst(item)
                    if hasattr(type(self), setterName):
                        # apparently, the setter method exists, so use it:
                        setter = getattr(type(self), setterName)
                        log.debug(function=setter, args=attrValue)
                        setter(self, attrValue)
                        break
                    else:
                        #nope, no setter method, so now we attempt to access the attribute directly
                        if hasattr(self, nm):
                            #apperently, the attr exists, so set its value directly by using setattr
                            log.debug("set: ", nm, " = ", attrValue)
                            setattr(self, nm, attrValue)
                            break
                        else:
                            log.warning(className, "does not have an attribute named:", item, "(", nm, ")")  
                            log.debug("\n\n", type(self), ".__dict__", self.__dict__, "\n\n")

    def addNestedElement(self, data, elementData):
        """
        Adds a nested element to data. A nested element is a serialized child object.
        Nested elements are named "elements" and its valu is a dict containing the 
        serialized attributes (marked as persistent) of the child object
        """
        d = data.copy()
        if not "elements" in d:
            d["elements"] = []
        d["elements"].append(elementData)
        #log.trace(type(self),".addNestedElement", (data, elementData), " --> ", d)
        return d

    def serialize(self):
        """
        serializes this instance to a dict of the following format:
        {type: qualified classname, class.attr1: value1, class.attr2: value2, ...}
        """
        data = {"type":self.getType()}
        data.update(self.getPersistentAttributes())
        return data

    def deserialize(self, data):
        """
        deserializes the provided data to this instance
        In effect, all persistent attributes of this instance, and its child 
        objects are set to the values stored in data
        """
        log.debug(function=self.deserialize, args=data)
        if self.isValidData(data):
            #self.initPersistentAttributes()

            # set the persistent attributes of this instance:
            self.setDataAttributes(data)

            elements = self.getDataElements(data)
            if elements:
                # iterate through the child objects
                for e in elements:
                    # e is a dict containing the persisted values of the persistent attributes of a single child object
                    className = self.getDataType(data) 
                    elementName = self.getDataType(e)
                    elementGetterName = "get"+self.getDataType(e)
                    elementAdderName = "add"+self.getDataType(e)
                    # try accessing the getter method for the collection of child objects
                    if hasattr(type(self), elementGetterName):
                        # apparently, the getter method exists, so use it to access the child object
                        getElement = getattr(type(self), elementGetterName)
                        element = getElement(self)
                        # verify that the found element is an instance of PersistentObject
                        assert isinstance(element, PersistentObject)
                        # now, recursively deserialize the child 
                        element.deserialize(e)
                    elif hasattr(type(self), elementAdderName):
                        # apparently, a getter does not exist, but an adder does, so use that to access the child
                        addElement = getattr(type(self), elementAdderName)
                        element = addElement(self)
                        # verify that the found element is an instance of PersistentObject
                        assert isinstance(element, PersistentObject)
                        # now, recursively deserialize the child 
                        element.deserialize(e)
                    else:
                        log.error("no getter or creator method found for element", 
                                  className + "." + elementName, 
                                  "\n\n", type(self), ".__dict__", type(self).__dict__, "\n\n")
        else: 
            assert False

