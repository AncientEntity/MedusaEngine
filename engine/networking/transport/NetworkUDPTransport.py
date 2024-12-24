import socket

from engine.logging import Log, LOG_WARNINGS, LOG_ERRORS
from engine.networking.connections.ClientConnectionUDP import ClientConnectionUDP
from engine.networking.transport.NetworkTransportBase import NetworkTransportBase


class NetworkUDPTransport(NetworkTransportBase):
    def __init__(self):
        super().__init__()
        self._socket : socket.socket = None

        self.targetServer : (str,int) = None

    def Open(self, ip: str, port: int) -> None:
        if self._socket:
            Log("Socket already exists.", LOG_WARNINGS)
            return

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((ip,port))
        self.active = True

    def Connect(self, targetServer : (str, int)):
        if self._socket:
            Log("Socket already exists.", LOG_WARNINGS)
            return
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.targetServer = targetServer
        self.active = True

    def Close(self):
        if not self._socket:
            Log("Socket doesnt exist.", LOG_ERRORS)
            return

        self._socket.close()
        self._socket = None
        self.active = False

    def Send(self, message, clientConnection : ClientConnectionUDP) -> None:
        if clientConnection:
            self._socket.sendto(message, clientConnection.address)
        else:
            self._socket.sendto(message, self.targetServer)

    def Receive(self, buffer=2048):
        return self._socket.recvfrom(buffer)