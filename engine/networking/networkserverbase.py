import threading

from engine.networking.connections.clientconnectionbase import ClientConnectionBase
from engine.networking.connections.clientconnectionsocket import ClientConnectionSocket
from engine.networking.transport.networktcptransport import NetworkTCPTransport
from engine.networking.transport.networktransportbase import NetworkTransportBase
from engine.networking.transport.networkudptransport import NetworkUDPTransport


class NetworkServerBase:
    def __init__(self):
        self.transportHandlers : dict[str, NetworkTransportBase] = {}

        self._messageQueue = []
        self._messageQueueLock = threading.Lock()

    def Open(self, layerName : str, connectionHandler : NetworkTransportBase, address : (str, int)):
        self.transportHandlers[layerName] = connectionHandler
        connectionHandler.Open(address[0], address[1])
        connectionHandler.receiveThread = threading.Thread(target=self.ThreadReceive, args=(connectionHandler,))
        connectionHandler.receiveThread.start()

    def Close(self, layerName):
        self.transportHandlers[layerName].Close()
        self.transportHandlers.pop(layerName)

    def Send(self, message, clientConnection : ClientConnectionBase, transportName):
        self.transportHandlers[transportName].Send(message, clientConnection)

    def SendAll(self, message, transportName):
        for clientConnection in self.transportHandlers[transportName].clientConnections[:]:
            try:
                self.transportHandlers[transportName].Send(message, clientConnection)
            except Exception as e:
                self.transportHandlers[transportName].clientConnections.remove(clientConnection)
                print(f"Error sending to client, possibly disconnected? {e}")

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