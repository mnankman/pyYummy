import wx
import styler

TILECOLORS = ["#333333", "#000066", "#CC0033", "#FF9933"]

def init():
    styleCat = styler.StyleCatalog.getInstance()
    
    """
    Style definitions for TileWidget
    """

    styleCat.addStyle(
        styleName = "TileWidget:base",
        elements=[
            wx.Font(20, family = wx.FONTFAMILY_MODERN, style = 0, weight = 100, 
                underline = False, faceName ="", encoding = wx.FONTENCODING_DEFAULT),
            wx.TRANSPARENT_PEN,
            wx.TRANSPARENT_BRUSH,
            styler.Colors(textForeground="White")
        ],
    )

    styleCat.addStyle(
        styleName = "TileWidget:black", 
        basedOn = "TileWidget:base",
        elements = [wx.Brush(TILECOLORS[0], style=wx.BRUSHSTYLE_SOLID)]
    )

    styleCat.addStyle(
        styleName = "TileWidget:blue", 
        basedOn = "TileWidget:base",
        elements = [wx.Brush(TILECOLORS[1], style=wx.BRUSHSTYLE_SOLID)]
    )

    styleCat.addStyle(
        styleName = "TileWidget:red", 
        basedOn = "TileWidget:base",
        elements = [wx.Brush(TILECOLORS[2], style=wx.BRUSHSTYLE_SOLID)]
    )

    styleCat.addStyle(
        styleName = "TileWidget:orange", 
        basedOn = "TileWidget:base",
        elements = [wx.Brush(TILECOLORS[3], style=wx.BRUSHSTYLE_SOLID)]
    )


    """
    Style definitions for TileSetWidget
    """
    
    styleCat.addStyle(
        styleName = "TileSetWidget:normal",
        elements=[
            wx.Font(8, family = wx.FONTFAMILY_MODERN, style = 0, weight = 100, 
                underline = False, faceName ="", encoding = wx.FONTENCODING_DEFAULT),
            wx.TRANSPARENT_PEN,
            wx.TRANSPARENT_BRUSH,
            styler.Colors(textForeground="White")
        ],
    )

    styleCat.addStyle(
        styleName = "TileSetWidget:mouseOver", 
        basedOn = "TileSetWidget:normal",
        elements = [wx.Brush("#CCCCCC", style=wx.BRUSHSTYLE_SOLID)]
    )

    styleCat.addStyle(
        styleName = "TileSetWidget:posIndicator", 
        basedOn = "TileSetWidget:normal",
        elements = [wx.Brush("Black", style=wx.BRUSHSTYLE_SOLID)]
    )

    styleCat.addStyle(
        styleName = "TileSetWidget:highlight", 
        basedOn = "TileSetWidget:normal",
        elements = [wx.Brush("White", style=wx.BRUSHSTYLE_SOLID)]
    )

    styleCat.addStyle(
        styleName = "TileSetWidget:modified", 
        basedOn = "TileSetWidget:normal",
        elements = [wx.Brush("#008800", style=wx.BRUSHSTYLE_SOLID)]
    )

    styleCat.addStyle(
        styleName = "TileSetWidget:modifiedHighlight", 
        basedOn = "TileSetWidget:normal",
        elements = [wx.Brush("#00FF00", style=wx.BRUSHSTYLE_SOLID)]
    )

    """
    Style definitions for PlayerWidget
    """

    styleCat.addStyle(
        styleName = "PlayerWidget:base",
        elements=[
            wx.Font(8, family = wx.FONTFAMILY_MODERN, style = 0, weight = 100, 
                underline = False, faceName ="", encoding = wx.FONTENCODING_DEFAULT),
            wx.TRANSPARENT_PEN,
            wx.TRANSPARENT_BRUSH,
            styler.Colors(textForeground="White")
        ],
    )

    styleCat.addStyle(
        styleName = "PlayerWidget:waiting", 
        basedOn = "PlayerWidget:base",
        elements = [wx.Brush("#000000", style=wx.BRUSHSTYLE_SOLID)]
    )

    styleCat.addStyle(
        styleName = "PlayerWidget:playing", 
        basedOn = "PlayerWidget:base",
        elements = [wx.Brush("#006633", style=wx.BRUSHSTYLE_SOLID)]
    )
