import socket
import threading

from engine.logging import Log, LOG_WARNINGS, LOG_ERRORS
from engine.networking.connections.clientconnectionsocket import ClientConnectionSocket
from engine.networking.transport.networktransportbase import NetworkTransportBase


class NetworkTCPTransport(NetworkTransportBase):
    def __init__(self):
        super().__init__()
        self._socket : socket.socket = None

        self.tcpRecvBuffer = 2048

        self.connections = []

        self._messageQueue = []
        self._queueLock : threading.Lock = threading.Lock()


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

        connection : ClientConnectionSocket
        for connection in self.connections:
            connection.Close()

        self.active = False

    def Send(self, message, clientConnection : ClientConnectionSocket) -> None:
        if clientConnection:
            clientConnection.tcpConnection.send(message)
        else:
            self._socket.send(message) # Probably client not server

    def ThreadAccept(self):
        while self.active:
            c, addr = self._socket.accept()
            clientConnection = ClientConnectionSocket()
            clientConnection.tcpConnection = c
            self.connections.append(clientConnection)

    def ThreadReceive(self, connection : ClientConnectionSocket) -> None:
        while connection.active:
            message = connection.tcpConnection.recv(self.tcpRecvBuffer)
            self._queueLock.acquire()
            self._messageQueue.append((message, connection))
            self._queueLock.release()

    def Receive(self):
        self._queueLock.acquire()
        message = self._messageQueue[0]
        self._messageQueue.pop(0)
        self._queueLock.release()
        return message