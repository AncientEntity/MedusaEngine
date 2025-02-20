import socket

from engine.logging import Log, LOG_WARNINGS, LOG_ERRORS
from engine.networking.connections.clientconnectionbase import ClientConnectionBase
from engine.networking.connections.clientconnectionsocket import ClientConnectionSocket
from engine.networking.transport.networktransportbase import NetworkTransportBase


class NetworkUDPTransport(NetworkTransportBase):
    def __init__(self):
        super().__init__()
        self._socket : socket.socket = None

        self.targetServer : (str,int) = None

        self._isServer = False

    def Open(self, ip: str, port: int) -> None:
        if self._socket:
            Log("Socket already exists.", LOG_WARNINGS)
            return

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((ip,port))
        self.active = True
        self._isServer = True

    def Connect(self, targetServer : (str, int)):
        if self._socket:
            Log("Socket already exists.", LOG_WARNINGS)
            return
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(("0.0.0.0",0))
        self.targetServer = targetServer
        self.active = True
        self._isServer = False

    def Close(self):
        if not self._socket:
            Log("Socket doesnt exist.", LOG_ERRORS)
            return

        self.active = False
        self._socket.close()
        self._socket = None
        self._isServer = False

    def Send(self, message, clientConnection : ClientConnectionSocket) -> None:
        if clientConnection:
            self._socket.sendto(message, clientConnection.address)
        else:
            self._socket.sendto(message, self.targetServer)

    def Receive(self, buffer=2048) -> (bytes, ClientConnectionBase):
        try:
            if self._isServer:
                recv = self._socket.recvfrom(buffer)
                c = ClientConnectionSocket()
                c.address = recv[1]
                return (recv[0], c)
            else:
                recv = self._socket.recv(buffer)
                return (recv, None)
        except Exception as e:
            if not self.active:
                return None
            else:
                raise e