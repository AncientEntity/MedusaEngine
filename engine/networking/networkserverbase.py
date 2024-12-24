import threading

from engine.networking.connections.clientconnectionbase import ClientConnectionBase
from engine.networking.connections.clientconnectionsocket import ClientConnectionSocket
from engine.networking.transport.networktcptransport import NetworkTCPTransport
from engine.networking.transport.networktransportbase import NetworkTransportBase
from engine.networking.transport.networkudptransport import NetworkUDPTransport


class NetworkServerBase:
    def __init__(self):
        self.transportHandlers : dict[str, NetworkTransportBase] = {}

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
        for clientConnection in self.transportHandlers[transportName].clientConnections:
            self.transportHandlers[transportName].Send(message, clientConnection)

    def ThreadReceive(self, transporter : NetworkTransportBase):
        while transporter.active:
            import time
            message = transporter.Receive(2048)
            print(message)
            transporter.Send(f"received{message}".encode(), message[1])
            time.sleep(1)

t = NetworkServerBase()
t.Open("tcp", NetworkTCPTransport(), ("127.0.0.1",25238))
while True:
    pass