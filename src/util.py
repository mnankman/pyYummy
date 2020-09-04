def rectsOverlap(r1, r2):
    x1,y1,w1,h1 = r1
    x2,y2,w2,h2 = r2
    if (x1>=x2+w2) or (x1+w1<=x2) or (y1+h1<=y2) or (y1>=y2+h2):
        return False
    else:
        return True

def insideRect(tup, rect):
    if len(tup) >= 2: 
        x1 = tup[0]
        y1 = tup[1]
        w1 = tup[2] if len(tup)>=3 else 0
        h1 = tup[3] if len(tup)>=4 else 0
        x2,y2,w2,h2 = rect
        if (x1>=x2) and (y1>=y2) and (x1+w1<=x2+w2) and (y1+h1<=y2+h2):
            return True
        else:
            return False
    else:
        return False

def filteredCount(function, collection):
    filtered = filter(function, collection)
    count = 0
    for item in filtered: count+=1
    return count

def toString(item):
    if hasattr(type(item), "toString"):
        return item.toString()
    else:
        return str(item)

def collectionToString(collection, itemtostr=lambda item: toString(item)):
    brackets = "()" if isinstance(collection, tuple) else "[]"
    s = brackets[0]
    n=0
    for item in collection:
        if isinstance(item, (tuple, list)):
            s += collectionToString(item, itemtostr)
        else:
            s += itemtostr(item)
        n+=1
        if n<len(collection): s += ","
    s += brackets[1]
    return s

def upperFirst(str):
    n = len(str)
    return str[0:1].upper() + str[1:]

def getKwargValue(name, *args, **kwargs):
    try:
        return kwargs[name]
    except KeyError:
        return None


if __name__ == "__main__":
    c = [1,1,1,2,1]
    print(filteredCount(lambda x: x>1, c))

    d = {
        1: 1,
        2: 1,
        3: 1,
        4: 2
    }

    print(filteredCount(lambda x: x>1, d.values()))

    print(collectionToString(c))
    
    print(collectionToString((1,2,3)))
    print(collectionToString([(1,2,3), 4, 5]))
    
    print(upperFirst("test"))

    def fun(arg, *args, **kwargs):
        for arg in kwargs.keys(): 
            print(arg, "=", getKwargValue(arg, **kwargs))
        print("D = ", getKwargValue("D", **kwargs))

    fun(0, A=False, B="test", C=[1,2,3])