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

        self._threadReceive : threading.Thread = None

        self._messageQueue = []
        self._messageQueueLock = threading.Lock()

    def Connect(self, layerName : str, connectionHandler : NetworkTransportBase, address : (str, int)):
        self.transportHandlers[layerName] = connectionHandler
        connectionHandler.Connect(address)
        connectionHandler.receiveThread = threading.Thread(target=self.ThreadReceive,args=(connectionHandler,))
        connectionHandler.receiveThread.name = f"CNetThreadRecv{layerName}"
        connectionHandler.receiveThread.start()

    def Close(self, layerName : str):
        self.transportHandlers[layerName].Close()
        self.transportHandlers.pop(layerName)

    def CloseAll(self):
        for transport in self.transportHandlers:
            self.Close(transport)

    def Send(self, message, transportName):
        self.transportHandlers[transportName].Send(message, None)

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

if __name__ == '__main__': # todo net remove before putting into master
    t = NetworkClientBase()
    t.Connect("tcp", NetworkTCPTransport(), ("127.0.0.1", 25238))
    while True:
        import random, time
        t.Send(f"test!{random.randint(0,999)}".encode(), "tcp")
        msg = None
        while not msg:
            msg = t.GetNextMessage()
        print(f"Reply: {msg[0].decode()}")
        time.sleep(0.5)