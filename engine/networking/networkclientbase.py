import threading

from engine.networking.connections.clientconnectionbase import ClientConnectionBase
from engine.networking.connections.clientconnectionsocket import ClientConnectionSocket
from engine.networking.transport.networktcptransport import NetworkTCPTransport
from engine.networking.transport.networktransportbase import NetworkTransportBase
from engine.networking.transport.networkudptransport import NetworkUDPTransport


class NetworkClientBase:
    def __init__(self):
        self.connection = None

        self.transportHandlers  : dict[str, NetworkTransportBase] = {}
        self._transportLayerCount = 0

        self._threadReceive : threading.Thread = None
        self._sendThread : threading.Thread = None

        self._messageQueue = []
        self._messageQueueLock = threading.Lock()

        self._outgoingQueue = []
        #self._outgoingQueueLock = threading.Lock()

    def Connect(self, layerName : str, connectionHandler : NetworkTransportBase, address : (str, int)):
        self.transportHandlers[layerName] = connectionHandler
        connectionHandler.Connect(address)
        connectionHandler.receiveThread = threading.Thread(target=self.ThreadReceive,args=(connectionHandler,))
        connectionHandler.receiveThread.name = f"CNetThreadRecv{layerName}"
        connectionHandler.receiveThread.start()

        self._transportLayerCount += 1
        #if not self._sendThread:
        #    self._sendThread = threading.Thread(target=self.ThreadSend, args=())
        #    self._sendThread.name = f"CNetThreadSend{layerName}"
        #    self._sendThread.start()

    def Close(self, layerName : str):
        self.transportHandlers[layerName].Close()

    def CloseAll(self):
        for transport in self.transportHandlers:
            self.Close(transport)

    def Send(self, message, transportName):
        #self._outgoingQueueLock.acquire()
        #self._outgoingQueue.append((transportName, message))
        #self._outgoingQueueLock.release()
        self.transportHandlers[transportName].Send(message, None)

    def ThreadSend(self):
        while self._transportLayerCount != 0:
            if len(self._outgoingQueue) == 0:
                continue
            #self._outgoingQueueLock.acquire()
            transportLayerName, data = self._outgoingQueue.pop(0)
            #self._outgoingQueueLock.release()
            self.transportHandlers[transportLayerName].Send(data, None)
            #print(f"c send: {transportLayerName}, {targetClient}, {data}")
        self._sendThread = None

    def ThreadReceive(self, transporter: NetworkTransportBase):
        while transporter.active:
            message = transporter.Receive(2048)
            self._messageQueueLock.acquire()
            self._messageQueue.append(message)
            self._messageQueueLock.release()

    def GetNextMessage(self):
        if len(self._messageQueue) == 0:
            return None

        self._messageQueueLock.acquire()
        message = self._messageQueue.pop(0)
        self._messageQueueLock.release()
        return message

if __name__ == '__main__': # todo remove before putting into master
    t = NetworkClientBase()
    t.Connect("tcp", NetworkTCPTransport(), ("127.0.0.1", 25238))
    while True:
        import random, time
        t.Send(f"test!{random.randint(0,999)}".encode(), "tcp")
        time.sleep(0.5)