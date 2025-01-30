from engine.networking.variables.networkvarbase import NetworkVarBase
import struct

class NetworkVarVector(NetworkVarBase):
    def __init__(self, entityId, defaultValue=[0,0]):
        super().__init__(entityId)
        self.value : list = defaultValue

        self.byteType = 'd' # either 'f' or 'd' to select float or double for byte serialization.
        self._dataSize = 8 if self.byteType == 'd' else 4

    def Set(self, value : list, modified=True):
        self.value = value
        super().Set(value, modified)
    def Get(self):
        return self.value


    def SetFromBytes(self, byteValue : bytes, modified=True):
        self.value = []
        for i in range(len(byteValue) // self._dataSize):
            floatBytes = byteValue[i*self._dataSize:i*self._dataSize+self._dataSize]
            if len(floatBytes) == 0:
                continue
            self.value.append(struct.unpack(self.byteType, floatBytes)[0])
        super().SetFromBytes(byteValue, modified)
    def GetAsBytes(self):
        byteArray = bytearray()
        for i in range(len(self.value)):
            byteArray.extend(struct.pack(self.byteType, float(self.value[i])))
        return byteArray


if __name__ == '__main__':
    t = NetworkVarVector(0)
    t.Set([-2.100,5.0,-2.9])
    s = t.GetAsBytes()
    print(s)
    t.SetFromBytes(s)
    print(t.Get())