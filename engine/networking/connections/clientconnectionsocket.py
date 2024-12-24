import socket

from engine.networking.connections.clientconnectionbase import ClientConnectionBase


class ClientConnectionSocket(ClientConnectionBase):
    def __int__(self, ip, port):
        super().__init__()

        self.address = (ip,port)
        self.tcpConnection : socket.socket = None

    def Close(self):
        if self.tcpConnection:
            self.tcpConnection.close()
        self.active = False