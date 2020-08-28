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

        def addStyle(self, *args, **kwargs):
            name = util.getKwargValue("styleName", **kwargs)
            assert name
            elements = util.getKwargValue("elements", **kwargs)
            assert elements
            basedOn = util.getKwargValue("basedOn", **kwargs)
            # start collecting the settings (colours, brushes, pens) for this style
            settings = None
            # copy the settings of the style this style is based on
            if basedOn: settings = self.getStyle(basedOn)
            if not settings: settings = {}
            #convert each setting to a tuple: (type, value)
            for el in elements:
                settings[type(el)] = el
            self.__styles__[name] = settings

        def getStyle(self, name):
            style = None
            if name in self.__styles__:
                if hasattr(type(self.__styles__[name]), "copy"):
                    style = self.__styles__[name].copy()
            if not style:
                log.warning(function=self.getStyle, args=name, returns=style)
            return style

    def getInstance():
        if not StyleCatalog.__instance__: StyleCatalog.__instance__ = StyleCatalog.__StyleCatalog__()
        return StyleCatalog.__instance__

class PaintStyler:
    def __init__(self):
        self.stylecat = StyleCatalog.getInstance()

    def select(self, name, dc):
        assert isinstance(dc, wx.DC)
        assert dc
        style = self.stylecat.getStyle(name)
        if style:
            assert isinstance(style, dict)
            for styleType, styleInstance in style.items():
                if styleType == wx.Pen: dc.SetPen(styleInstance)
                if styleType == wx.Brush: dc.SetBrush(styleInstance)
                if styleType == wx.Font: dc.SetFont(styleInstance)
                if styleType == Colors: 
                    if styleInstance.textForeground: dc.SetTextForeground(styleInstance.textForeground)
                    if styleInstance.textBackground: dc.SetTextBackground(styleInstance.textBackground)
 

                