from engine.networking.connections.clientconnectionbase import ClientConnectionBase


class NetworkTransportBase:
    def __init__(self):
        self.active = False
        self.clientConnections = []

        self.receiveThread = None
        self.receiveProcess = None

        # When server has connections/disconnects
        self.onClientConnect = [] # func(ClientConnectionBase)
        self.onClientDisconnect = [] # func(ClientConnectionBase)

        self.onDisconnect = [] # func() # When client disconnects

    def Connect(self):
        pass
    def Open(self, ip : str, port : int):
        pass
    def Close(self):
        pass
    def Kick(self, clientConnection : ClientConnectionBase):
        pass

    def Send(self, message, clientConnection : ClientConnectionBase):
        pass
    def Receive(self, buffer=2048) -> tuple[bytes, ClientConnectionBase]:
        pass

    def CallHook(self, hookArray, args):
        for hook in hookArray:
            hook(*args)