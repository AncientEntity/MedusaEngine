import socket, time

from engine.networking.connections.clientconnectionbase import ClientConnectionBase


class ClientConnectionSocket(ClientConnectionBase):
    def __init__(self, ip, port):
        super().__init__()

        self.address = (ip,port)
        self.tcpConnection : socket.socket = None
        self.nickname = f"{ip}:{port}"

        self.udpHeartbeat = time.time()

    def Close(self):
        if self.tcpConnection:
            self.tcpConnection.close()
        self.active = False