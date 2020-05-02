import sys
import socket
import selectors
import types
import sys
import getopt
from console import AbstractConsole, TerminalConsole
import threading
from model import ServerModel

BUFSIZE = 1024

class Server:
    def __init__(self, host, port, console=None):
        self.model = ServerModel()
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        if console==None:
            self.console = TerminalConsole()
        else:
            self.console = console

    def _print(self, *args):
        self.console.print("[server] ", *args)

    def acceptConnection(self, sock):
        conn, address = sock.accept()
        self._print("accepted connection from address: ", address)
        conn.setblocking(False)
        self.model.connectMessageBox(address)
        data = types.SimpleNamespace(addr=address, inb=b"", outb=b"")
        self.sel.register(conn, selectors.EVENT_READ|selectors.EVENT_WRITE, data=data)

    def update(self, key):
        sock = key.fileobj
        data = key.data
        data.outb = self.model.getAllMessages(data.addr)
        self.model.clearMessages(data.addr)
        self.sel.modify(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)  

    def exchange(self, key, mask):
        self.update(key)
        self.receive(key, mask)
        self.send(key, mask)

    def close(self, key):
        self._print("closing connection to address: ", key.data.addr)
        self.sel.unregister(key.fileobj)
        key.fileobj.close()

    def receive(self, key, mask):
        if mask & selectors.EVENT_READ:
            sock = key.fileobj
            data = key.data
            try:
                buf = sock.recv(BUFSIZE)
                if buf: 
                    #data.outb += repr(buf)
                    self.model.receiveMessage(buf)
                    self._print("received ", repr(buf), "from address: ", data.addr)
                else:
                    self._print("No data received")
                    self.close(key)
            except ConnectionResetError:
                self._print("Connection with client lost")
                self.close(key)


    def send(self, key, mask):
        if mask & selectors.EVENT_WRITE:
            sock = key.fileobj
            data = key.data
            if data.outb:
                self._print("sending ", data.outb, "to address: ", data.addr)
                try:
                    sent = sock.send(data.outb)
                    data.outb = data.outb[sent:]
                except OSError:
                    self._print ("Error while sending to ", data.addr)
                    self._print("closing connection to address: ", data.addr)
                    self.sel.unregister(sock)
                    sock.close()

    def stop(self):
        self.sel.close()
        self.listeningSock.close()

    def start(self):
        self.listeningSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listeningSock.bind((self.host, self.port))
        self.listeningSock.listen()
        self._print("server listening on", (self.host, self.port))
        self.listeningSock.setblocking(False)
        self.sel.register(self.listeningSock, selectors.EVENT_READ, data=None)
        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.acceptConnection(key.fileobj)
                    else:
                        self.exchange(key, mask)
        except KeyboardInterrupt:
            self._print("key pressed, stopping server")
        finally:
            self.stop()

    def startThread(self):
        self.thread = threading.Thread(target=self.start)
        self.thread.start()

if __name__ == "__main__":
    helpTxt = "server.py -h <server hostname/ip-address> -p <server port>"
    serverHost = "127.0.0.1"
    serverPort = "65432"
    try:
        argv = sys.argv[1:]
        opts, args = getopt.getopt(argv,"?h:p:",["shost=","sport="])
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

    server = Server(serverHost, int(serverPort))
    server.start()
