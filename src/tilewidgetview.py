import wx
from tilewidget import TileWidget
import draggable 
import log

class TileWidgetView(draggable.DraggablePanel):
    def __init__(self, parent, draggable=False, portable=False, *args, **kwargs):
        super().__init__(parent, draggable, portable, *args, **kwargs)
        self.parent = parent
        self.__dropTargets__ = {}
        # by default, this instance is a drop target of itself
        #self.addTileWidgetDropTarget(self)
            
    def getObjectsByType(self, type):
        result = []
        children = self.GetChildren()
        for c in children:
            if isinstance(c, type):
                result.append(c)
        return result

    def getTileWidgets(self):
        return self.getObjectsByType(TileWidget)

    def addTileWidget(self, tileWidget):
        if self.__dropTargets__:
            for target, enabled in self.__dropTargets__.items():
                if enabled:
                    self.bindToTileWidgetDraggableEvents(target, tileWidget)

    def bindToTileWidgetDraggableEvents(self, target, tileWidget):
        assert tileWidget
        assert isinstance(tileWidget, TileWidget)
        #log.debug(function=self.bindToTileWidgetDraggableEvents, args=(target,tileWidget.tile))
        tileWidget.Bind(draggable.EVT_DRAGGABLE_HOVER, target.onTileHover)
        tileWidget.Bind(draggable.EVT_DRAGGABLE_RELEASE, target.onTileRelease)

    def findTileWidgetById(self, tId):
        result = None
        for tw in self.getTileWidgets():
            if tId==tw.tile.id():
                result = tw
                break
        if not result:
            log.error(function=self.findTileWidgetById, args=tId, returns=result)
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
 
    def onTileHover(self, event):
        pass

    def getEventPosition(self, event):
        return self.ScreenToClient(event.pos)

    def getEventObjectPosition(self, event):
        return self.ScreenToClient(event.obj.GetScreenPosition())

    def getEventObjectRect(self, event):
        x,y = self.getEventObjectPosition(event)
        w,h = event.obj.GetSize()
        log.debug(function=self.getEventObjectRect, args=event, returns=(x,y,w,h))
        return (x, y, w, h)

    def onTileRelease(self, event):
        log.debug(type(self), ".onTileRelease(", event.pos, ",", event.obj.tile.toString())
        if isinstance(event.obj, TileWidget):
            tileWidget = event.obj
            #for now, the default actions is to reject any tilewidget that is dropped on it
            #subclasses should override this method to implement specific behaviour 
            tileWidget.reject()

