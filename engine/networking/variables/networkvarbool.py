from engine.constants import NET_NONE
from engine.logging import Log
from engine.networking.variables.networkvarbase import NetworkVarBase
import struct

class NetworkVarBool(NetworkVarBase):
    def __init__(self, defaultValue=False):
        super().__init__()
        self.value : bool = defaultValue

    def Set(self, value: bool, modified=True):
        self.value = value
        super().Set(value, modified)
    def Add(self, value, modified=True):
        Log("Cannot add a network variable boolean.")
    def Get(self):
        return self.value


    def SetFromBytes(self, byteValue: bytes, modified=True):
        self.value = struct.unpack("?", byteValue)[0]
        super().SetFromBytes(byteValue, modified)
    def GetAsBytes(self):
        return struct.pack("?", self.value)
        #return self.value.to_bytes(8, byteorder='big')