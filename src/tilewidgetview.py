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
        self.__tileWidgets__ = []
            
    def sendNewTileWidget(self, tw):
        assert isinstance(tw, TileWidget)
        event = AddTileWidgetEvent(obj=tw)
        wx.PostEvent(self, event)
            
    def sendDestroyTileWidget(self, tw):
        assert isinstance(tw, TileWidget)
        event = DestroyTileWidgetEvent(obj=tw)
        wx.PostEvent(self, event)

    def getTileWidgets(self):
        return self.__tileWidgets__

    def addTileWidget(self, tileWidget):
        self.__tileWidgets__.append(tileWidget)
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
        if self.getTileWidgets() != None:
            for tileWidget in self.getTileWidgets():
                tileWidget.Destroy()
        self.__tileWidgets__ = []

