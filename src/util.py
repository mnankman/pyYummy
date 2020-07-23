def rectsOverlap(r1, r2):
    x1,y1,w1,h1 = r1
    x2,y2,w2,h2 = r2
    if (x1>=x2+w2) or (x1+w1<=x2) or (y1+h1<=y2) or (y1>=y2+h2):
        return False
    else:
        return True

def filteredCount(function, collection):
    filtered = filter(function, collection)
    count = 0
    for item in filtered: count+=1
    return count

def collectionToString(collection, itemtostr=lambda item: str(item)):
    s = "["
    n=0
    for item in collection:
        s += itemtostr(item)
        n+=1
        if n<len(collection): s += ","
    s += "]"
    return s

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