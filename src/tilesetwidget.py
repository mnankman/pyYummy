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
#        super().__init__(parent=parent, style=wx.TRANSPARENT_WINDOW)
        super().__init__(parent, True)
        self.set = set
        self.highlight = False
        self.newTilePos = None
        self.paintStyler = PaintStyler()

        self.font = wx.Font(8, family = wx.FONTFAMILY_MODERN, style = 0, weight = 100, 
            underline = False, faceName ="", encoding = wx.FONTENCODING_DEFAULT) 
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.Bind(wx.EVT_PAINT,self.onPaint)
        self.Bind(draggable.EVT_DRAGGABLE_RELEASE, self.onDragRelease)
        self.set.subscribe(self, "msg_object_modified", self.onMsgSetModified)
        
    def getStateStr(self):
        stateStr = str(self.set.getSize())
        if self.newTilePos != None:
            stateStr += ","+str(self.newTilePos)
        return stateStr

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

    def draw(self,dc):
        if self.highlight:
            if self.set.isModified():
                self.paintStyler.select("TileSetWidget:modifiedHighlight", dc)
            else:
                self.paintStyler.select("TileSetWidget:highlight", dc)
        else:
            if self.set.isModified():
                self.paintStyler.select("TileSetWidget:modified", dc)
            else:
                self.paintStyler.select("TileSetWidget:normal", dc)
        tw,th = TileWidget.defaultSize()
        w,h = self.GetClientSize()
        dc.DrawRoundedRectangle(0,0,w,th+10,6)
        dc.DrawText(self.getStateStr(), 3, th+12)

    def updateSize(self):
        tw,th = TileWidget.defaultSize()
        w,h = self.GetClientSize()
        self.SetSize(self.set.getSize()*tw+6, th+30)
    
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
        tw = int(w/self.set.getSize()) #calculated width of a tile based on widget size and number of tiles currently in the set
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
        xOffset = 3
        for tId in self.set.getOrder():
            tileWidget = self.findTileWidgetById(tId)
            if tileWidget and not(tileWidget.isBeingDragged()):
                w,h = tileWidget.GetSize()
                tileWidget.Move((xOffset, 3))
                tileWidget.Refresh()
                xOffset = xOffset + w 
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
            tileWidget.Reparent(self)
            self.highlight = False
            self.Refresh()
        self.newTilePos = None
        self.refreshLayout()

    def onMsgSetModified(self, payload):
        log.debug(function=self.onMsgSetModified, args=payload)
        self.update()
        self.refreshLayout()
        

