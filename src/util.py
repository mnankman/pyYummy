def rectsOverlap(r1, r2):
    x1,y1,w1,h1 = r1
    x2,y2,w2,h2 = r2
    if (x1>=x2+w2) or (x1+w1<=x2) or (y1+h1<=y2) or (y1>=y2+h2):
        return False
    else:
        return True
