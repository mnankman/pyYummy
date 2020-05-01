import sys
import socket
import selectors
import types
import threading

BUFSIZE = 1024

class Client:
    def __init__(self, host, port, name):
        self.name = name
        self.serverAddress = (host, port)
        self.sel = selectors.DefaultSelector()

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
        print("stopping client")
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
                print(buf.decode("utf-8"))
                data.recv_total += len(buf)
#            if not buf or data.recv_total == data.msg_total:
            if not buf:
                print("closing connection: ", data.connid)
                self.sel.unregister(sock)
                sock.close()

    def send(self, key, mask):
        if mask & selectors.EVENT_WRITE:
            sock = key.fileobj
            data = key.data
            if data.outb:
                #print("sending ", repr(data.outb), "to connection: ", data.connid)
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
            break
        client.message(message)


if __name__ == "__main__":
    name = input("type your name:")
    client = Client('127.0.0.1', 65430, name)
    t = threading.Thread(target=userInputThread, args=(client,))
    t.start()
    client.start()

    #client2 = Client('192.168.0.171', 51192)
