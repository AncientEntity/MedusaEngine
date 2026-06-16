import threading

from engine.logging import LOG_NETWORKPROCESS, Log
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
        self._messagesAvailable = threading.Semaphore(0)

    def Open(self, layerName : str, connectionHandler : NetworkTransportBase, address : (str, int)):
        self.transportHandlers[layerName] = connectionHandler
        connectionHandler.Open(address[0], address[1])
        connectionHandler.receiveThread = threading.Thread(target=self.ThreadReceive, args=(connectionHandler,), daemon=True)
        connectionHandler.receiveThread.name = f"SNetThreadRecv{layerName}"
        connectionHandler.receiveThread.start()

    def Close(self, layerName):
        self.transportHandlers[layerName].Close()
        self.transportHandlers.pop(layerName)

    def Send(self, message, clientConnection : ClientConnectionBase, transportName):
        self.transportHandlers[transportName].Send(message, clientConnection)

    def SendAll(self, message, transportName, ignoreTargets=[]):
        for clientConnection in self.transportHandlers[transportName].clientConnections[:]:
            if clientConnection.referenceId in ignoreTargets:
                continue

            try:
                self.transportHandlers[transportName].Send(message, clientConnection)
            except Exception as e:
                if clientConnection in self.transportHandlers[transportName].clientConnections:
                    self.transportHandlers[transportName].clientConnections.remove(clientConnection)
                Log(f"Error sending to client, possibly disconnected? {e}", LOG_NETWORKPROCESS)

    def ThreadReceive(self, transporter : NetworkTransportBase):
        while transporter.active:
            message = transporter.Receive(8192)
            self._messageQueueLock.acquire()
            self._messageQueue.append(message)
            self._messageQueueLock.release()
            self._messagesAvailable.release()

    def GetNextMessage(self) -> tuple[bytes, ClientConnectionBase]:
        self._messagesAvailable.acquire()

        self._messageQueueLock.acquire()
        message = self._messageQueue.pop(0)
        self._messageQueueLock.release()
        return message

if __name__ == '__main__':
    t = NetworkServerBase()
    t.Open("udp", NetworkUDPTransport(), ("127.0.0.1",25238))
    while True:
        next = t.GetNextMessage()
        if next:
            print(next[0].decode())
            t.Send(f"Reply: {next[0].decode()}".encode(), next[1], "udp")