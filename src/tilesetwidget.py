import wx
import draggable
from tilewidgetview import TileWidgetView
import model
import util
from styler import PaintStyler
from tilewidget import TileWidget

from log import Log
log = Log()

class TileSetWidget(TileWidgetView):  
    normalPenColor = 'Black'
    highlightPenColor = 'White'
    modifiedPenColor = '#008800'
    modifiedHighlightPenColor = '#00FF00'
    def __init__(self, parent, set):
        super().__init__(parent, True)
        self.set = set
        self.highlight = False
        self.mouseOver = False
        self.newTilePos = None
        self.NewTilePosList = []
        self.paintStyler = PaintStyler()

        self.Bind(wx.EVT_PAINT,self.onPaint)
        self.Bind(draggable.EVT_DRAGGABLE_RELEASE, self.onDragRelease)
        self.Bind(wx.EVT_ENTER_WINDOW, self.onMouseEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
        self.set.subscribe(self, "msg_object_modified", self.onMsgSetModified)

    def getStateStr(self):
        stateStr = str(self.set.getSize())
        if self.newTilePos != None:
            stateStr += ","+str(self.newTilePos)
        return stateStr

    def onMouseEnter(self, event):
        self.mouseOver = True
        self.Refresh()

    def onMouseLeave(self, event):
        self.mouseOver = False
        self.Refresh()

    def onDragRelease(self, event):
        x,y = event.pos
        self.setPos((x,y))

    def onPaint(self, event):
        event.Skip()
        #dc = wx.BufferedPaintDC(self)
        if self.set.isModified():
            self.updateSize()
        dc = wx.PaintDC(self)
        self.draw(dc)
        self.drawTilePosIndicator(dc)

    def draw(self, dc):
        if self.highlight:
            if self.set.isModified():
                self.paintStyler.select("TileSetWidget:modifiedHighlight", dc)
            else:
                self.paintStyler.select("TileSetWidget:highlight", dc)
        else:
            if self.set.isModified():
                self.paintStyler.select("TileSetWidget:modified", dc)
            elif self.mouseOver:
                self.paintStyler.select("TileSetWidget:mouseOver", dc)
            else:
                self.paintStyler.select("TileSetWidget:normal", dc)
        tw,th = TileWidget.defaultSize()
        w,h = self.GetClientSize()
        dc.DrawRectangle(0,h-5,w,h)

    def drawTilePosIndicator(self, dc):
        if self.newTilePos and len(self.NewTilePosList)>=self.newTilePos:
            self.paintStyler.select("TileSetWidget:posIndicator", dc)
            tw,th = TileWidget.defaultSize()
            w,h = self.GetClientSize()
            p = self.newTilePos-1
            ix,iy = (self.NewTilePosList[p], h-5)
            dc.DrawPolygon([(ix,iy),(ix-5,h),(ix+5,h)])


    def updateSize(self):
        tw,th = TileWidget.defaultSize()
        numTiles = self.set.getSize()
        self.SetSize(numTiles*tw+10, th+10)
    
    def setPos(self, pos):
        if pos:
            self.Move(pos)
            if self.set and isinstance(self.set, model.Set):
                self.set.setPos(pos)

    def update(self):
        self.Move(self.set.getPos())
        
    def getTilePosInSet(self, pos, tileWidget):
        posInSet = 1
        w,h = self.GetSize()
        tx,ty = pos #coordinates of hovering or dropped tile
        sx,sy = self.set.getPos()
        mx,my = self.ScreenToClient(wx.GetMousePosition())
        
        rx = tx-sx #the relative x-pos of the dropped tile within the set
        n = self.set.getSize()
        tw = int(w/n) if n>0 else 0 #calculated width of a tile based on widget size and number of tiles currently in the set
        if tw>0:
            posInSet = int((rx-0.5*tw)/tw)+2
        
        return posInSet
      
    def rebuild(self):
        for tile in self.set.getOrderedTiles():
            tileWidget = TileWidget(self, tile)
            self.addTileWidget(tileWidget)
            tileWidget.Bind(draggable.EVT_DRAGGABLE_HOVER, self.GetParent().onTileHover)
            tileWidget.Bind(draggable.EVT_DRAGGABLE_RELEASE, self.GetParent().onTileRelease)  
        self.refreshLayout()
    
    def refreshLayout(self):
        tw,th = TileWidget.defaultSize()
        xOffset = 5
        self.NewTilePosList = [xOffset]
        for tId in self.set.getOrder():
            tileWidget = self.findTileWidgetById(tId)
            if tileWidget and not(tileWidget.isBeingDragged()):
                w,h = tileWidget.GetSize()
                tileWidget.Move((xOffset, 3))
                tileWidget.Refresh()
                xOffset = xOffset + w 
                self.NewTilePosList.append(xOffset)
        self.updateSize()


    def onTileHover(self, event):
        tile = event.obj.tile
        if util.rectsOverlap(event.obj.GetRect(), self.GetRect()) and self.set.tileFitPosition(tile)>0:
            self.highlight = True
            self.newTilePos = self.getTilePosInSet(event.pos, event.obj)
        else:
            self.highlight = False
            self.newTilePos = None
        self.Refresh()

    def onTileRelease(self, event):
        tileWidget = event.obj
        tile = event.obj.tile
        x,y = event.pos
        self.newTilePos = self.getTilePosInSet(event.pos, event.obj)
        if tile.move(self.set, self.newTilePos):
            tileWidget.accept(self)
            self.highlight = False
            self.Refresh()
        else:
            tileWidget.reject()
        self.newTilePos = None
        self.refreshLayout()

    def onMsgSetModified(self, payload):
        log.debug(function=self.onMsgSetModified, args=payload)
        self.update()
        self.refreshLayout()
        

