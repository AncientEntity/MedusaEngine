from engine.networking.connections.clientconnectionbase import ClientConnectionBase


class NetworkTransportBase:
    def __init__(self):
        self.active = False
        self.clientConnections = []

    def Connect(self):
        pass
    def Open(self, ip : str, port : int):
        pass
    def Close(self):
        pass

    def Send(self, message, clientConnection : ClientConnectionBase):
        pass
    def Receive(self, buffer=2048) -> (bytes, ClientConnectionBase):
        pass