import wx
from console import AbstractConsole
import client

ID_NEWCHAT=101
ID_JOINCHAT=102
ID_CONNECT=103
ID_EXIT=200

class ChatPanel(wx.Panel):    
    def __init__(self, parent):
        super().__init__(parent=parent, size=(800,700))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.textConsole = wx.TextCtrl(self, 1, style=wx.TE_MULTILINE|wx.TE_READONLY , size=(800,700))
        self.sizer.Add(self.textConsole, 1, wx.EXPAND)

    def print(self, *args):
        line = ""
        for a in args:
            line = line + a
        self.textConsole.write(line+"\n")

class ClientFrame(wx.Frame):    
    def __init__(self):
        super().__init__(parent=None, title='Chat Client')
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel = ChatPanel(self)
        self.sizer.Add(self.panel, 1, wx.EXPAND)
        self.create_menu()
#        self.create_toolbar(self.sizer)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Centre()
        self.Show()
        self.exitDialog = wx.MessageDialog( self, "Exit? \n",
                        "GOING away ...", wx.YES_NO)

    def create_menu(self):
        menuBar = wx.MenuBar()
        connectMenu = wx.Menu()
        connectMenu.Append(ID_CONNECT, "&Connect", "Connect to chat server")
        connectMenu.Append(ID_EXIT, "E&xit", "Exit")
        chatMenu = wx.Menu()
        chatMenu.Append(ID_NEWCHAT, "&New", "Start new chat")
        chatMenu.Append(ID_JOINCHAT, "&Join", "Join existing chat")
        menuBar.Append(connectMenu, "&Connect")
        menuBar.Append(chatMenu, "C&hat")
        self.SetMenuBar(menuBar)

        self.Bind(event=wx.EVT_MENU, handler=self.OnConnect, id=ID_CONNECT)
        self.Bind(event=wx.EVT_MENU, handler=self.OnExit, id=ID_EXIT)
        self.Bind(event=wx.EVT_MENU, handler=self.OnNew, id=ID_NEWCHAT)
        self.Bind(event=wx.EVT_MENU, handler=self.OnJoin, id=ID_JOINCHAT)

    def OnConnect(self, e):
        serverHost = "127.0.0.1"
        serverPort = 65432
        alias = "mark"
        self.client = client.Client(serverHost, serverPort, alias, self.panel)
        self.client.startThread()

    def OnExit(self, e):
        answer = self.exitDialog.ShowModal()
        if answer == wx.ID_YES:
            self.Close(True) 

    def OnNew(self, e):
        pass

    def OnJoin(self, e):
        pass

if __name__ == '__main__':
    app = wx.App()
    cf = ClientFrame()
    app.MainLoop()
