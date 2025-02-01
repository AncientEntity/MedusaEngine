from engine.networking.connections.clientconnectionbase import ClientConnectionBase


class NetworkTransportBase:
    def __init__(self):
        self.active = False
        self.clientConnections = []

        self.receiveThread = None
        self.receiveProcess = None

    def Connect(self):
        pass
    def Open(self, ip : str, port : int):
        pass
    def Close(self):
        pass

    def Send(self, message, clientConnection : ClientConnectionBase):
        pass
    def Receive(self, buffer=2048) -> tuple[bytes, ClientConnectionBase]:
        pass