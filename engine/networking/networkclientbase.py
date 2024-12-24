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

    def Connect(self, layerName : str, connectionHandler : NetworkTransportBase, address : (str, int)):
        self.transportHandlers[layerName] = connectionHandler
        connectionHandler.Connect(address)

    def Close(self, layerName : str):
        self.transportHandlers[layerName].Close()

    def Send(self, message, transportName):
        self.transportHandlers[transportName].Send(message, None)

    def ThreadReceive(self, transporter: NetworkTransportBase):
        while transporter.active:
            message = transporter.Receive(2048)
            print(message.decode())

t = NetworkClientBase()
t.Connect("tcp", NetworkTCPTransport(), ("127.0.0.1", 25238))
while True:
    import random
    t.Send(f"test!{random.randint(0,999)}".encode(), "tcp")