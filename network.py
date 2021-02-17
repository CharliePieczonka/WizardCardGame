import socket
import pickle


class network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # CHANGE THIS VALUE TO THE SERVER HOST'S IPv4 ADDRESS
        self.server = "192.168.0.62"
        # **************************************************

        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)

            # not unpickling because when we initially connect we're just getting the player number
            return self.client.recv(2048).decode()
        except:
            pass

    def send(self, data):
        try:
            # send string data to server and receive object
            # self.client.send(str.encode(data))
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048*2048))
        except socket.error as e:
            print(e)

    def recv(self):
        return self.client.recv(2048).decode()