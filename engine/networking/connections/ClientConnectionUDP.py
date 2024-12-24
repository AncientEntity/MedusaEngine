from engine.networking.connections.ClientConnectionBase import ClientConnectionBase


class ClientConnectionUDP(ClientConnectionBase):
    def __int__(self, ip, port):
        self.address = (ip,port)