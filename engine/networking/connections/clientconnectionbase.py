


class ClientConnectionBase:
    referenceIdIncrementer = 0
    def __init__(self):
        self.active = True
        self.referenceId = ClientConnectionBase.referenceIdIncrementer
        ClientConnectionBase.referenceIdIncrementer += 1