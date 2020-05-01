import sys
import socket
import selectors
import types
import threading
import sys
import getopt
import server
from console import AbstractConsole, TerminalConsole

BUFSIZE = 1024

class Client:
    def __init__(self, host, port, name, console=None):
        self.name = name
        self.serverAddress = (host, port)
        self.sel = selectors.DefaultSelector()
        if console==None:
            self.console = TerminalConsole()
        else:
            self.console = console

    def _print(self, *args):
        self.console.print("[client] ", *args)

    def connect(self):
        msg = self.name + ": connected\n"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.connect_ex(self.serverAddress)
        data = types.SimpleNamespace(
            connid=1,
            msg_total=len(msg),
            recv_total=0,
            outb=msg.encode("utf-8"),
        )
        self.sel.register(self.sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)  

    def message(self, message):
        msg = self.name + ": " + message + "\n"
        data = types.SimpleNamespace(
            connid=1,
            msg_total=len(msg),
            recv_total=0,
            outb=msg.encode("utf-8"),
        )
        self.sel.modify(self.sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)  

    def close(self):
        self._print("stopping client")
        self.sel.unregister(self.sock)
        self.sock.close()

    def exchange(self, key, mask):
        self.send(key, mask)
        self.receive(key, mask)

    def receive(self, key, mask):
        if mask & selectors.EVENT_READ:
            sock = key.fileobj
            data = key.data
            buf = sock.recv(BUFSIZE)
            if buf: 
                self._print(buf.decode("utf-8"))
                data.recv_total += len(buf)
#            if not buf or data.recv_total == data.msg_total:
            if not buf:
                self._print("closing connection: ", data.connid)
                self.sel.unregister(sock)
                sock.close()

    def send(self, key, mask):
        if mask & selectors.EVENT_WRITE:
            sock = key.fileobj
            data = key.data
            if data.outb:
                #self._print("sending ", repr(data.outb), "to connection: ", data.connid)
                sent = sock.send(data.outb)
                data.outb = data.outb[sent:]

    def start(self):     
        try:
            self.connect()
            while True:
                events = self.sel.select(timeout=1)
                if events:
                    for key, mask in events:
                        self.exchange(key, mask)
                # Check for a socket being monitored to continue.
                if not self.sel.get_map():
                    break
        finally:
            self.sel.close()

def userInputThread(client):
    print("type 'quit' or 'exit' to exit")
    while True:
        message = input("")
        if message=="quit" or message=="exit":
            client.close()
            sys.exit()
        client.message(message)

def integratedServerThread(host, port):
    s = server.Server(host, port)
    s.start()

if __name__ == "__main__":
    helpTxt = "client.py -h <server hostname/ip-address> -p <server port> -a <alias> -i"
    serverHost = "127.0.0.1"
    serverPort = "65432"
    integratedServer = False
    alias = ""
    try:
        argv = sys.argv[1:]
        opts, args = getopt.getopt(argv,"?ih:p:a:",["shost=","sport=","alias="])
    except getopt.GetoptError:
        print (helpTxt)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-?':
            print (helpTxt)
            sys.exit()
        elif opt in ("-h", "--shost"):
            serverHost = arg
        elif opt in ("-p", "--sport"):
            serverPort = arg
        elif opt in ("-a", "--alias"):
            alias = arg
        elif opt == '-i':
            integratedServer = True

    if integratedServer:
        inServer = server.Server(serverHost, int(serverPort))
        ist = threading.Thread(target=inServer.start)
        ist.start()

    if (alias==""): 
        alias = input("type your name:")
    client = Client(serverHost, int(serverPort), alias)
    uit = threading.Thread(target=userInputThread, args=(client,))
    uit.start()
    client.start()

    
