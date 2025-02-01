import threading

from engine.networking.connections.clientconnectionbase import ClientConnectionBase
from engine.networking.connections.clientconnectionsocket import ClientConnectionSocket
from engine.networking.transport.networktcptransport import NetworkTCPTransport
from engine.networking.transport.networktransportbase import NetworkTransportBase
from engine.networking.transport.networkudptransport import NetworkUDPTransport

import time

class NetworkServerBase:
    def __init__(self):
        self.transportHandlers : dict[str, NetworkTransportBase] = {}
        self._transportLayerCount = 0

        self._messageQueue = []
        self._messageQueueLock = threading.Lock()

        self._outgoingQueue = []
        #self._outgoingQueueLock = threading.Lock()
        self.sendThread = None

    def Open(self, layerName : str, connectionHandler : NetworkTransportBase, address : (str, int)):
        self.transportHandlers[layerName] = connectionHandler
        connectionHandler.Open(address[0], address[1])
        connectionHandler.receiveThread = threading.Thread(target=self.ThreadReceive, args=(connectionHandler,))
        connectionHandler.receiveThread.name = f"SNetThreadRecv{layerName}"
        connectionHandler.receiveThread.start()

        self._transportLayerCount += 1
        #if not self.sendThread:
        #    self.sendThread = threading.Thread(target=self.ThreadSend, args=())
        #    self.sendThread.name = f"SNetThreadSend{layerName}"
        #    self.sendThread.start()

    def Close(self, layerName):
        self.transportHandlers[layerName].Close()
        self.transportHandlers.pop(layerName)
        self._transportLayerCount -= 1

    def Send(self, message, clientConnection : ClientConnectionBase, transportName):
        #self._outgoingQueueLock.acquire()
        #self._outgoingQueue.append((transportName, clientConnection, message))
        #self._outgoingQueueLock.release()
        self.transportHandlers[transportName].Send(message, clientConnection)

    def SendAll(self, message, transportName):
        for clientConnection in self.transportHandlers[transportName].clientConnections[:]:
            try:
                self.Send(message, clientConnection, transportName)
                #self.transportHandlers[transportName].Send(message, clientConnection)
            except Exception as e:
                self.transportHandlers[transportName].clientConnections.remove(clientConnection)
                print(f"Error sending to client, possibly disconnected? {e}")

    def ThreadSend(self):
        while self._transportLayerCount != 0:
            if len(self._outgoingQueue) == 0:
                continue
            #self._outgoingQueueLock.acquire()
            transportLayerName, targetClient, data = self._outgoingQueue.pop(0)
            #self._outgoingQueueLock.release()
            self.transportHandlers[transportLayerName].Send(data, targetClient)
            #print(f"s send: {transportLayerName}, {targetClient}, {data}")
        self.sendThread = None

    def ThreadReceive(self, transporter : NetworkTransportBase):
        while transporter.active:
            message = transporter.Receive(2048)
            self._messageQueueLock.acquire()
            self._messageQueue.append(message)
            self._messageQueueLock.release()

    def GetNextMessage(self) -> tuple[bytes, ClientConnectionBase]:
        if len(self._messageQueue) == 0:
            return None

        self._messageQueueLock.acquire()
        message = self._messageQueue.pop(0)
        self._messageQueueLock.release()
        return message

if __name__ == '__main__': # todo remove before putting into master
    t = NetworkServerBase()
    t.Open("tcp", NetworkTCPTransport(), ("127.0.0.1",25238))
    while True:
        pass