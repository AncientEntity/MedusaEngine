import socket
import threading

from engine.logging import Log, LOG_WARNINGS, LOG_ERRORS
from engine.networking.connections.clientconnectionsocket import ClientConnectionSocket
from engine.networking.transport.networktransportbase import NetworkTransportBase


class NetworkTCPTransport(NetworkTransportBase):
    def __init__(self):
        super().__init__()
        self._socket : socket.socket = None

        self.connections = []

        self._messageQueue = []
        self._queueLock : threading.Lock = threading.Lock()

        self.clientReceiveThread = None


    def Open(self, ip: str, port: int, listenCount=10) -> None:
        if self._socket:
            Log("Socket already exists.", LOG_WARNINGS)
            return

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((ip,port))
        self._socket.listen(listenCount)
        self.active = True

        acceptThread = threading.Thread(target=self.ThreadAccept)
        acceptThread.start()

    def Connect(self, targetServer : (str, int)):
        if self._socket:
            Log("Socket already exists.", LOG_WARNINGS)
            return
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect(targetServer)
        self.active = True

        self.clientReceiveThread = threading.Thread(target=self.ThreadReceiveClient)
        self.clientReceiveThread.start()

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
            clientConnection.tcpConnection.send(len(message).to_bytes(4, byteorder='big'))
            clientConnection.tcpConnection.send(message)
        else:
            self._socket.send(len(message).to_bytes(4, byteorder='big')) # Probably client not server
            self._socket.send(message) # Probably client not server

    def ThreadAccept(self):
        while self.active:
            print("AWAITING")
            c, addr = self._socket.accept()
            print("CONNECTION")
            clientConnection = ClientConnectionSocket()
            clientConnection.tcpConnection = c
            self.connections.append(clientConnection)
            receiveThread = threading.Thread(target=self.ThreadReceiveListener, args=(clientConnection,))
            receiveThread.start()


    def ThreadReceiveListener(self, connection : ClientConnectionSocket) -> None:
        while connection.active:
            messageSize = int.from_bytes(connection.tcpConnection.recv(4),byteorder='big')
            message = connection.tcpConnection.recv(messageSize)
            self._queueLock.acquire()
            self._messageQueue.append((message, connection))
            self._queueLock.release()

    def ThreadReceiveClient(self):
        while self._socket:
            messageSize = int.from_bytes(self._socket.recv(4),byteorder='big')
            message = self._socket.recv(messageSize)
            self._queueLock.acquire()
            self._messageQueue.append((message, None))
            self._queueLock.release()



    def Receive(self, buffer=2048):
        while len(self._messageQueue) == 0:
            continue

        self._queueLock.acquire()
        message = self._messageQueue[0]
        self._messageQueue.pop(0)
        self._queueLock.release()
        return message