import socket

from engine.logging import Log, LOG_WARNINGS, LOG_ERRORS
from engine.networking.connections.clientconnectionsocket import ClientConnectionSocket
from engine.networking.transport.networktransportbase import NetworkTransportBase


class NetworkTCPTransport(NetworkTransportBase):
    def __init__(self):
        super().__init__()
        self._socket : socket.socket = None

        self.connections = []


    def Open(self, ip: str, port: int, listenCount=10) -> None:
        if self._socket:
            Log("Socket already exists.", LOG_WARNINGS)
            return

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((ip,port))
        self._socket.listen(listenCount)
        self.active = True

    def Connect(self, targetServer : (str, int)):
        if self._socket:
            Log("Socket already exists.", LOG_WARNINGS)
            return
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect(targetServer)
        self.active = True

    def Close(self):
        if not self._socket:
            Log("Socket doesnt exist.", LOG_ERRORS)
            return

        self._socket.close()
        self._socket = None
        self.active = False

    def Send(self, message, clientConnection : ClientConnectionSocket) -> None:
        if clientConnection:
            self._socket.sendto(message, clientConnection.address)
        else:
            self._socket.send(message)

    def ThreadAccept(self):
        # todo temporary solution
        c, addr = self._socket.accept()
        self.connections.append(c)

    def Receive(self, buffer=2048):
        return self._socket.recv(buffer)