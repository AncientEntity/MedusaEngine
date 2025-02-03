import socket
import threading
import time

from engine.logging import Log, LOG_WARNINGS, LOG_ERRORS
from engine.networking.connections.clientconnectionsocket import ClientConnectionSocket
from engine.networking.transport.networktransportbase import NetworkTransportBase


class NetworkTCPTransport(NetworkTransportBase):
    def __init__(self):
        super().__init__()
        self._socket : socket.socket = None

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
        acceptThread.name = "SNetThreadAccept"
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

        self.active = False

        self._socket.close()
        self._socket = None

        connection : ClientConnectionSocket
        for connection in self.clientConnections:
            connection.Close()

    def Send(self, message, clientConnection : ClientConnectionSocket) -> None:
        if clientConnection:
            clientConnection.tcpConnection.send(len(message).to_bytes(4, byteorder='big')+message)
            #clientConnection.tcpConnection.send(message)
        else:
            self._socket.send(len(message).to_bytes(4, byteorder='big')+message) # Probably client not server
            #self._socket.send(message) # Probably client not server

    def ThreadAccept(self):
        while self.active:
            try:
                c, addr = self._socket.accept()
            except Exception as e:
                if not self.active:
                    return
                else:
                    raise e
            clientConnection = ClientConnectionSocket()
            clientConnection.tcpConnection = c
            self.clientConnections.append(clientConnection)
            self.CallHook(self.onClientConnect, (clientConnection,))
            receiveThread = threading.Thread(target=self.ThreadReceiveListener, args=(clientConnection,))
            receiveThread.start()


    def ThreadReceiveListener(self, connection : ClientConnectionSocket) -> None:
        while connection.active:
            try:
                messageSize = int.from_bytes(connection.tcpConnection.recv(4),byteorder='big')
                message = connection.tcpConnection.recv(messageSize)
            except Exception:
                Log(f"Error receiving from client: {connection.referenceId}, assuming disconnect.")
                connection.Close()
                if connection in self.clientConnections:
                    self.clientConnections.remove(connection)
                self.CallHook(self.onClientDisconnect, (connection,))
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
            if not self.active:
                return None

        self._queueLock.acquire()
        message = self._messageQueue.pop(0)
        self._queueLock.release()
        return message