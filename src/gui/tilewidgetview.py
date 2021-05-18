import wx
from lib import log
from gui.tilewidget import TileWidget
from gui import draggable 
from base.tile import Tile

class TileWidgetView(draggable.DraggableDropTarget):
    def __init__(self, parent, draggable=False, portable=False, zoomfactor=1, *args, **kwargs):
        super().__init__(parent, draggable, portable, *args, **kwargs)
        self.parent = parent
        self.zoomfactor = zoomfactor
        self.__dropTargets__ = {}
        # by default, this instance is a drop target of itself
        #self.addTileWidgetDropTarget(self)
            
    def setZoomFactor(self, zoomfactor):
        self.zoomfactor = zoomfactor
        self.Refresh()

    def getZoomFactor(self):
        if hasattr(self.parent, "zoomfactor"):
            return self.zoomfactor * self.parent.getZoomFactor()
        else:
            return self.zoomfactor
    
    def getObjectsByType(self, type):
        result = []
        children = self.GetChildren()
        for c in children:
            if isinstance(c, type):
                result.append(c)
        return result

    def getTileWidgets(self):
        return self.getObjectsByType(TileWidget)

    def addTileWidget(self, tile):
        assert isinstance(tile, Tile)
        tileWidget = TileWidget(self, tile)
        if self.__dropTargets__:
            for target, enabled in self.__dropTargets__.items():
                if enabled:
                    target.bindToDraggableEvents(tileWidget)
        return tileWidget

    def findTileWidgetById(self, tId):
        result = None
        for tw in self.getTileWidgets():
            if tId==tw.tile.id():
                result = tw
                break
        if not result:
            log.warning(function=self.findTileWidgetById, args=tId, returns=result)
        return result
 
    def resetTileWidgets(self):
        children = self.GetChildren()
        for c in children:
            if isinstance(c, TileWidget):
                c.Destroy()

    def addTileWidgetDropTarget(self, target, enabled=True):
        assert isinstance (target, TileWidgetView)
        self.__dropTargets__[target] = enabled

    def enableTileWidgetDropTarget(self, target, enabled=True):
        assert isinstance (target, TileWidgetView)
        self.__dropTargets__[target] = enabled
 
    def onDraggableHover(self, event):
        if isinstance(event.obj, TileWidget):
            self.onTileHover(event)
        super().onDraggableHover(event)

    def onDraggableRelease(self, event):
        if isinstance(event.obj, TileWidget):
            self.onTileRelease(event)
        super().onDraggableRelease(event)

    def onDraggableAccept(self, event):
        super().onDraggableAccept(event)

    def onTileHover(self, event):
        pass

    def onTileRelease(self, event):
        log.debug(type(self), ".onTileRelease(", event.pos, ",", event.obj.tile.toString())
        if isinstance(event.obj, TileWidget):
            tileWidget = event.obj
            #for now, the default actions is to reject any tilewidget that is dropped on it
            #subclasses should override this method to implement specific behaviour 
            tileWidget.reject()

    def getEventPosition(self, event):
        return self.ScreenToClient(event.pos)

    def getEventObjectPosition(self, event):
        return self.ScreenToClient(event.obj.GetScreenPosition())

    def getEventObjectRect(self, event):
        x,y = self.getEventObjectPosition(event)
        w,h = event.obj.GetSize()
        log.debug(function=self.getEventObjectRect, args=event, returns=(x,y,w,h))
        return (x, y, w, h)


