import wx
from tilewidget import TileWidget
from draggable import DraggablePanel

from log import Log
log = Log()

import wx.lib.newevent
AddTileWidgetEvent, EVT_TILEWIDGETVIEW_ADD = wx.lib.newevent.NewEvent()
DestroyTileWidgetEvent, EVT_TILEWIDGETVIEW_DESTROY = wx.lib.newevent.NewEvent()

class TileWidgetView(DraggablePanel):
    def __init__(self, parent, draggable=False, *args, **kwargs):
        super().__init__(parent, draggable, *args, **kwargs)
            
    def sendNewTileWidget(self, tw):
        assert isinstance(tw, TileWidget)
        event = AddTileWidgetEvent(obj=tw)
        wx.PostEvent(self, event)
            
    def sendDestroyTileWidget(self, tw):
        assert isinstance(tw, TileWidget)
        event = DestroyTileWidgetEvent(obj=tw)
        wx.PostEvent(self, event)

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
        self.sendNewTileWidget(tileWidget)

    def findTileWidgetById(self, tId):
        tw = None
        for c in self.GetChildren():
            if isinstance(c, TileWidget):
                if tId==c.tile.id():
                    tw = c
                    break
        if not tw:
            log.error(function=self.findTileWidgetById, args=tId, returns=tw)
        return tw
 
    def resetTileWidgets(self):
        tileWidgets = self.getTileWidgets()
        if tileWidgets != None:
            for tileWidget in tileWidgets:
                tileWidget.Destroy()

