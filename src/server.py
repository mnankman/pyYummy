import sys
import socket
import selectors
import types

BUFSIZE = 1024

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.received = []
        self.messageBoxes = {}

    def acceptConnection(self, sock):
        conn, address = sock.accept()
        print("accepted connection from address: ", address)
        conn.setblocking(False)
        self.messageBoxes[address] = []
        data = types.SimpleNamespace(addr=address, inb=b"", outb=b"")
        self.sel.register(conn, selectors.EVENT_READ|selectors.EVENT_WRITE, data=data)

    def update(self, key):
        sock = key.fileobj
        data = key.data
        for m in self.messageBoxes[data.addr]:
            data.outb += m
        self.messageBoxes[data.addr] = []
        self.sel.modify(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)  

    def exchange(self, key, mask):
        self.update(key)
        self.receive(key, mask)
        self.send(key, mask)

    def close(self, key):
        print("closing connection to address: ", key.data.addr)
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
                    for addr in self.messageBoxes:
                        self.messageBoxes[addr].append(buf)
                    print("received ", repr(buf), "from address: ", data.addr)
                else:
                    print("No data received")
                    self.close(key)
            except ConnectionResetError:
                print("Connection with client lost")
                self.close(key)


    def send(self, key, mask):
        if mask & selectors.EVENT_WRITE:
            sock = key.fileobj
            data = key.data
            if data.outb:
                print("sending ", data.outb, "to address: ", data.addr)
                try:
                    sent = sock.send(data.outb)
                    data.outb = data.outb[sent:]
                except OSError:
                    print ("Error while sending to ", data.addr)
                    print("closing connection to address: ", data.addr)
                    self.sel.unregister(sock)
                    sock.close()

    def stop(self):
        self.sel.close()
        self.listeningSock.close()

    def start(self):
        self.listeningSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listeningSock.bind((self.host, self.port))
        self.listeningSock.listen()
        print("server listening on", (self.host, self.port))
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
            print("key pressed, stopping server")
        finally:
            self.stop()

if __name__ == "__main__":

    server = Server('127.0.0.1', 65430)
    server.start()
