from engine.networking.variables.networkvarbase import NetworkVarBase


class NetworkVarInt(NetworkVarBase):
    def __init__(self, entityId, defaultValue=0):
        super().__init__(entityId)
        self.value : int = defaultValue

    def Set(self, value, modified=True):
        self.value = value
        super().Set(value, modified)
    def Get(self):
        return self.value


    def SetFromBytes(self, byteValue : bytes, modified=True):
        self.value = int.from_bytes(byteValue, byteorder='big')
        super().SetFromBytes(byteValue, modified)
    def GetAsBytes(self):
        return self.value.to_bytes(4, byteorder='big')