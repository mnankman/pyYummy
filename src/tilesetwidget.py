import wx
import draggable
import model
import util
from tilewidget import TileWidget

class TileSetWidget(draggable.DraggablePanel):  
    normalPenColor = 'Black'
    highlightPenColor = 'White'
    modifiedPenColor = '#008800'
    modifiedHighlightPenColor = '#00FF00'
    def __init__(self, parent, set):
#        super().__init__(parent=parent, style=wx.TRANSPARENT_WINDOW)
        super().__init__(parent=parent)
        self.set = set
        self.highlight = False
        self.newTilePos = None
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
            tw,th = TileWidget.defaultSize()

            w,h = self.GetClientSize()
            self.SetSize(len(self.set.getTiles())*36+6, h)
            self.SetSize(self.set.getSize()*36+6, th+30)

            self.updateSize()
        dc = wx.PaintDC(self)
        self.draw(dc)

    def draw(self,dc):
        if self.highlight:
            if self.set.isModified():
                dc.SetPen(wx.Pen(TileSetWidget.modifiedHighlightPenColor, 1, wx.PENSTYLE_DOT))
            else:
                dc.SetPen(wx.Pen(TileSetWidget.highlightPenColor, 1, wx.PENSTYLE_DOT))
        else:
            if self.set.isModified():
                dc.SetPen(wx.Pen(TileSetWidget.modifiedPenColor, 1, wx.PENSTYLE_DOT))
            else:
                dc.SetPen(wx.Pen(TileSetWidget.normalPenColor, 1, wx.PENSTYLE_DOT))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        tw,th = TileWidget.defaultSize()
        w,h = self.GetClientSize()
        dc.DrawRoundedRectangle(0,0,w,th+10,6)
        dc.SetFont(self.font) 
        dc.SetTextForeground("white")
        dc.DrawText(self.getStateStr(), 3, th+12)

    def updateSize(self):
        tw,th = TileWidget.defaultSize()
        w,h = self.GetClientSize()
        self.SetSize(self.set.getSize()*36+6, th+30)
    
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
        tile = event.obj.tile
        x,y = event.pos
        self.newTilePos = self.getTilePosInSet(event.pos, event.obj)
        if tile.move(self.set, self.newTilePos):
            #self.updateSize()
            self.highlight = False
            self.Refresh()
        self.newTilePos = None

    def onMsgSetModified(self, payload):
        self.update()
        

