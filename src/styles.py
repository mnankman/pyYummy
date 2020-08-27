import wx
import styler

def init():
    styleCat = styler.StyleCatalog.getInstance()
    
    styleCat.setStyle(
        wx.Font(8, family = wx.FONTFAMILY_MODERN, style = 0, weight = 100, 
            underline = False, faceName ="", encoding = wx.FONTENCODING_DEFAULT),
        wx.TRANSPARENT_PEN,
        wx.TRANSPARENT_BRUSH,
        styler.Colors(textForeground="White"),
        styleName = "TileSetWidget:normal"
    )

    styleCat.setStyle(
        wx.Pen("Black", 1, wx.PENSTYLE_DOT),
        styleName = "TileSetWidget:mouseOver", 
        basedOn = "TileSetWidget:normal"
    )

    styleCat.setStyle(
        wx.Pen("Black", 2, wx.PENSTYLE_SOLID),
        styleName = "TileSetWidget:posIndicator", 
        basedOn = "TileSetWidget:normal"
    )

    styleCat.setStyle(
        wx.Brush("White", style=wx.BRUSHSTYLE_SOLID),
        styleName = "TileSetWidget:highlight", 
        basedOn = "TileSetWidget:normal"
    )

    styleCat.setStyle(
        wx.Brush("#008800", style=wx.BRUSHSTYLE_SOLID),
        styleName = "TileSetWidget:modified", 
        basedOn = "TileSetWidget:normal"
    )

    styleCat.setStyle(
        wx.Brush("#00FF00", style=wx.BRUSHSTYLE_SOLID),
        styleName = "TileSetWidget:modifiedHighlight", 
        basedOn = "TileSetWidget:normal"
    )