from engine.networking.connections.clientconnectionbase import ClientConnectionBase


class ClientConnectionSocket(ClientConnectionBase):
    def __int__(self, ip, port):
        self.address = (ip,port)