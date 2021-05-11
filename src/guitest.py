import asyncio

import wx
from wxasync import WxAsyncApp
from wx.lib.inspection import InspectionTool

from lib import log

from gui import styles, draggable

RESOURCES="src/resource"
ID_EXIT=200
ID_DRAGGABLE_TEST = 301
ID_SHOWINSPECTIONTOOL=600

class MainWindow(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='GUI Test', size=(500,500))
        styles.init()

        #iconFile = RESOURCES+"/yummy-icon-28-white.png"
        #icon = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
        #self.SetIcon(icon)

        self.frames = []

        self.createMenu()

        self.Show()
        self.Bind(event=wx.EVT_CLOSE, handler=self.onUserCloseMainWindow)

    def createMenu(self):
        menuBar = wx.MenuBar()
        debugMenu = wx.Menu()
        debugMenu.Append(ID_SHOWINSPECTIONTOOL, "&Inspection tool", "Show the WX Inspection Tool")
        fileMenu = wx.Menu()
        fileMenu.Append(ID_EXIT, "E&xit", "Exit")
        testMenu = wx.Menu()
        testMenu.Append(ID_DRAGGABLE_TEST, "&Draggable Test", "Draggable Test")
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(debugMenu, "&Debug")
        menuBar.Append(testMenu, "&Test")
        self.SetMenuBar(menuBar)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserExit, id=ID_EXIT)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserShowInspectionTool, id=ID_SHOWINSPECTIONTOOL)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserDraggableTest, id=ID_DRAGGABLE_TEST)

    def closeAllTests(self):
        for f in self.frames:
            try:
                f.Close()
            finally:
                pass
    
    def onUserCloseMainWindow(self, e):
        self.closeAllTests()
        exit()
        e.Skip()

    def onUserExit(self, e):
        self.Close(True) 
        e.Skip()

    def onUserShowInspectionTool(self, e):
        InspectionTool().Show()
        e.Skip()

    def closeFrame(self, f, e):
        if f in self.frames:
            i = self.frames.index(f)
            self.frames.pop(i)
        e.Skip()

    def addFrame(self, f):
        assert isinstance(f, wx.Frame)
        self.frames.append(f)
        f.Bind(event=wx.EVT_CLOSE, handler=lambda e: self.closeFrame(f, e))

    def onUserDraggableTest(self, e):
        f = draggable.DraggableDropFrame(parent=None, title='Draggable Test', size=(500,500))
        self.addFrame(f)

        basePanel = draggable.DraggableDropTarget(f, False, name="base")
        basePanel.SetBackgroundColour("#000000")

        target1 = draggable.DraggableDropTarget(basePanel, True, False, name="target1", pos=(20,20), size=(200,200), style=wx.CLIP_CHILDREN)
        target1.SetBackgroundColour("#444444")

        target2 = draggable.DraggableDropTarget(basePanel, True, True, name="target2", pos=(300,300), size=(100,100), style=wx.CLIP_CHILDREN)
        target2.SetBackgroundColour("#004400")

        target3 = draggable.DraggableDropTarget(basePanel, True, True, name="target3", pos=(20,300), size=(100,100), style=wx.CLIP_CHILDREN)
        target3.SetBackgroundColour("#440000")

        draggable1 = draggable.DraggablePanel(target1, True, False, name="draggable1", pos=(5,5), size=(30,30), style=wx.CLIP_CHILDREN)
        draggable1.SetBackgroundColour("#880000")

        draggable2 = draggable.DraggablePanel(target1, True, True, name="draggable2", pos=(50,50), size=(50,50), style=wx.CLIP_CHILDREN)
        draggable2.SetBackgroundColour("#008800")

        f.bindToDraggableEvents(draggable2)
        basePanel.bindToDraggableEvents(target2)
        target1.bindToDraggableEvents(draggable2)
        target1.bindToDraggableEvents(target2)
        target2.bindToDraggableEvents(draggable2)
        target3.bindToDraggableEvents(draggable2)

        f.Show()
        e.Skip()


import logging

def start():
    logging.basicConfig(format='[%(name)s] %(levelname)s:%(message)s', level=logging.DEBUG)
    app = WxAsyncApp()
    loop = asyncio.get_event_loop()
    w = MainWindow()
    try:
        loop.run_until_complete(app.MainLoop())
    finally:
        loop.stop()
        loop.close()

if __name__ == '__main__':
    start()
