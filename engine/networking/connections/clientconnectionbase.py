


class ClientConnectionBase:
    referenceIdIncrementer = 0
    def __init__(self):
        self.active = True
        self.referenceId = ClientConnectionBase.referenceIdIncrementer
        self.nickname : str = "unknown" # Should be set to ip/port or steamID, etc.
        ClientConnectionBase.referenceIdIncrementer += 1