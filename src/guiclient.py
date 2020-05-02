import wx
from console import AbstractConsole
import client
import server

ID_NEWCHAT=101
ID_JOINCHAT=102
ID_STARTSERVER=103
ID_CONNECT=104
ID_EXIT=200
ID_SENDMESSAGE=500

class ConsolePanel(wx.Panel):    
    def __init__(self, parent):
        super().__init__(parent=parent, size=(400,300))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.textConsole = wx.TextCtrl(self, 1, style=wx.TE_MULTILINE|wx.TE_READONLY , size=(400,300))
        self.textConsole.SetBackgroundColour(wx.BLACK)
        self.textConsole.SetDefaultStyle(wx.TextAttr(wx.WHITE, wx.BLACK))
        font = wx.Font(wx.FontInfo(8))
        self.textConsole.SetFont(font)
        self.sizer.Add(self.textConsole, 1)
        self.SetSizer(self.sizer)

    def print(self, *args):
        line = ""
        for a in args:
            line = line + str(a)
        self.textConsole.write(line+"\n")
        self.textConsole.MarkDirty()

class ChatPanel(wx.Panel):    
    def __init__(self, parent):
        super().__init__(parent=parent, size=(400,700))
        self.client = client
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.chatInputBox = wx.TextCtrl(self, 1, style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER, size=(400, 100))
        self.chatInputBox.SetBackgroundColour(wx.LIGHT_GREY)
        self.chatInputBox.SetDefaultStyle(wx.TextAttr(wx.BLACK, wx.LIGHT_GREY))
        font = wx.Font(wx.FontInfo(12))
        self.chatInputBox.SetFont(font)
        hbox1.Add(self.chatInputBox, 1, wx.EXPAND)
        vbox.Add(hbox1)
        self.chatInputBox.Bind(event=wx.EVT_TEXT_ENTER, handler=self.OnEnter)
        self.SetSizer(vbox)
        self.connected = False

    def setClient(self, client):
        self.client = client
        self.connected = True

    def OnEnter(self, e):
        print ("Enter pressed")
        if self.connected:
            self.client.message(e.GetString())
            self.chatInputBox.Clear()

class ClientFrame(wx.Frame):    
    def __init__(self):
        super().__init__(parent=None, title='Chat Client')
        self.serverHost = "127.0.0.1"
        self.serverPort = 65432
        self.client = None
        self.server = None

        vsplitter = wx.SplitterWindow(self, -1)
        self.chatPanel = ChatPanel(vsplitter)
        hsplitter = wx.SplitterWindow(vsplitter, -1)
        self.clientConsolePanel = ConsolePanel(hsplitter)
        self.serverConsolePanel = ConsolePanel(hsplitter)
        hsplitter.SplitHorizontally(self.clientConsolePanel, self.serverConsolePanel)
        vsplitter.SplitVertically(self.chatPanel, hsplitter)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(vsplitter, 1, wx.EXPAND)
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
        connectMenu.Append(ID_STARTSERVER, "&Start integrated server", "Start the integrated server")
        connectMenu.Append(ID_CONNECT, "&Connect", "Connect to chat server")
        connectMenu.Append(ID_EXIT, "E&xit", "Exit")
        chatMenu = wx.Menu()
        chatMenu.Append(ID_NEWCHAT, "&New", "Start new chat")
        chatMenu.Append(ID_JOINCHAT, "&Join", "Join existing chat")
        menuBar.Append(connectMenu, "&Connect")
        menuBar.Append(chatMenu, "C&hat")
        self.SetMenuBar(menuBar)

        self.Bind(event=wx.EVT_MENU, handler=self.OnStartServer, id=ID_STARTSERVER)
        self.Bind(event=wx.EVT_MENU, handler=self.OnConnect, id=ID_CONNECT)
        self.Bind(event=wx.EVT_MENU, handler=self.OnExit, id=ID_EXIT)
        self.Bind(event=wx.EVT_MENU, handler=self.OnNew, id=ID_NEWCHAT)
        self.Bind(event=wx.EVT_MENU, handler=self.OnJoin, id=ID_JOINCHAT)

    def OnConnect(self, e):
        alias = "mark"
        self.client = client.Client(self.serverHost, self.serverPort, alias, self.clientConsolePanel)
        self.client.startThread()
        self.chatPanel.setClient(self.client)

    def OnStartServer(self, e):
        self.server = server.Server(self.serverHost, self.serverPort, self.serverConsolePanel)
        self.server.startThread()


    def OnExit(self, e):
        #answer = self.exitDialog.ShowModal()
        #if answer == wx.ID_YES:
        if True:
            if self.client != None:
                self.client.close()
            if self.server != None:
                self.server.stop()
            self.Close(True) 

    def OnNew(self, e):
        pass

    def OnJoin(self, e):
        pass

if __name__ == '__main__':
    app = wx.App()
    cf = ClientFrame()
    app.MainLoop()
