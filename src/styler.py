import wx
import util

from log import Log
log = Log()

class Colors:
    def __init__(self, *args, **kwargs):
        self.background = util.getKwargValue("background", **kwargs)
        self.foreground = util.getKwargValue("foreground", **kwargs)
        self.textForeground = util.getKwargValue("textForeground", **kwargs)
        self.textBackground = util.getKwargValue("textBackground", **kwargs)

class StyleCatalog:
    __instance__ = None

    class __StyleCatalog__:
        def __init__(self):
            self.__styles__ = {}

        def setStyle(self, *args, **kwargs):
            name = util.getKwargValue("styleName", **kwargs)
            assert name
            basedOn = util.getKwargValue("basedOn", **kwargs)
            styles = None
            if basedOn: styles = self.getStyle(basedOn)
            if not styles: styles = {}
            for style in args:
                styles[type(style)] = style
            self.__styles__[name] = styles

        def getStyle(self, name):
            style = None
            if name in self.__styles__:
                if hasattr(type(self.__styles__[name]), "copy"):
                    style = self.__styles__[name].copy()
            log.debug(function=self.getStyle, args=name, returns=style)
            return style

    def getInstance():
        if not StyleCatalog.__instance__: StyleCatalog.__instance__ = StyleCatalog.__StyleCatalog__()
        return StyleCatalog.__instance__

class PaintStyler:
    def __init__(self):
        self.stylecat = StyleCatalog.getInstance()

    def select(self, name, dc):
        log.debug(function=self.select, args=(name, dc))
        assert isinstance(dc, wx.DC)
        assert dc
        style = self.stylecat.getStyle(name)
        if style:
            log.debug(var=("style",style))
            assert isinstance(style, dict)
            for styleType, styleInstance in style.items():
                if styleType == wx.Pen: dc.SetPen(styleInstance)
                if styleType == wx.Brush: dc.SetBrush(styleInstance)
                if styleType == wx.Font: dc.SetFont(styleInstance)
                if styleType == Colors: 
                    if styleInstance.textForeground: dc.SetTextForeground(styleInstance.textForeground)
                    if styleInstance.textBackground: dc.SetTextBackground(styleInstance.textBackground)
 

                