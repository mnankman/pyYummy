import wx
import styler

def init():
    styler.StyleCatalog.getInstance().setStyle(
        wx.Pen("Black", 1, wx.PENSTYLE_DOT),
        wx.Font(8, family = wx.FONTFAMILY_MODERN, style = 0, weight = 100, 
            underline = False, faceName ="", encoding = wx.FONTENCODING_DEFAULT),
        wx.TRANSPARENT_BRUSH,
        styler.Colors(textForeground="White"),
        styleName = "TileSetidget:normal"
    )

    styler.StyleCatalog.getInstance().setStyle(
        wx.Pen("White", 1, wx.PENSTYLE_DOT),
        styleName = "TileSetWidget:highlight", 
        basedOn = "TileSetWidget:normal"
    )

    styler.StyleCatalog.getInstance().setStyle(
        wx.Pen('#008800', 1, wx.PENSTYLE_DOT),
        styleName = "TileSetWidget:modified", 
        basedOn = "TileSetWidget:normal"
    )

    styler.StyleCatalog.getInstance().setStyle(
        wx.Pen('#00FF00', 1, wx.PENSTYLE_DOT),
        styleName = "TileSetWidget:modifiedHighlight", 
        basedOn = "TileSetWidget:normal"
    )