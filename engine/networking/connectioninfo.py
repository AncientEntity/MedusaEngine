from engine.networking.connections.clientconnectionbase import ClientConnectionBase


class ConnectionInfo:
    def __init__(self, clientId, connection : ClientConnectionBase):
        self.clientID = clientId
        self.connection = connection