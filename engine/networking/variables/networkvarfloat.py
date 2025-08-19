from engine.networking.variables.networkvarbase import NetworkVarBase
import struct

class NetworkVarFloat(NetworkVarBase):
    def __init__(self, defaultValue=0.0):
        super().__init__()
        self.value : float = defaultValue

    def Set(self, value : float, modified=True):
        self.value = value
        super().Set(value, modified)
    def Add(self, value, modified=True):
        self.value += value
        super().Add(value, modified)
    def Get(self):
        return self.value


    def SetFromBytes(self, byteValue : bytes, modified=True):
        self.value = struct.unpack(">d", byteValue)[0]
        super().SetFromBytes(byteValue, modified)
    def GetAsBytes(self):
        return struct.pack(">d", self.value)
        #return self.value.to_bytes(8, byteorder='big')