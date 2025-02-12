from engine.networking.variables.networkvarbase import NetworkVarBase
import struct

from engine.tools.math import Distance


class WrappedList(list):
    def __init__(self, iterable, interp, netVar):
        super().__init__(iterable)
        self.interp = interp
        self.netVar = netVar
    def __getitem__(self, item):
        if not self.netVar._modified:
            return self.interp[item]
        return super().__getitem__(item)
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.interp[key] = value
        self.netVar._modified = True

class NetworkVarVector(NetworkVarBase):
    def __init__(self, defaultValue=[0,0]):
        super().__init__()
        self.value : list = defaultValue

        self.minSize = 2
        self.minByteChangeDifference = None

        self.byteType = 'd' # either 'f' or 'd' to select float or double for byte serialization.
        self._dataSize = 8 if self.byteType == 'd' else 4

    def Set(self, value : list, modified=True):
        self.value = list(value) if isinstance(value, tuple) else value
        while len(self.value) < self.minSize:
            self.value.append(0.0)
        super().Set(value, modified)
    def Add(self, value, modified=True):
        for i in range(len(self.value)):
            self.value[i] += value[i]
        super().Add(value, modified)
    def Get(self):
        return WrappedList(self.value, self.value, self)
    def GetExact(self):
        return tuple(self.value) # Return immutable tuple to prevent issues with it not being a WrappedList.

    def SetFromBytes(self, byteValue : bytes, modified=True):
        newValue = []
        for i in range(len(byteValue) // self._dataSize):
            floatBytes = byteValue[i*self._dataSize:i*self._dataSize+self._dataSize]
            if len(floatBytes) == 0:
                continue
            newValue.append(struct.unpack(self.byteType, floatBytes)[0])
        while len(newValue) < self.minSize:
            newValue.append(0.0)

        if self.minByteChangeDifference != None and Distance(self.value, newValue) < self.minByteChangeDifference:
            return

        self.value = newValue
        super().SetFromBytes(byteValue, modified)
    def GetAsBytes(self):
        byteArray = bytearray()
        for i in range(len(self.value)):
            byteArray.extend(struct.pack(self.byteType, float(self.value[i])))
        return byteArray


if __name__ == '__main__':
    t = NetworkVarVector()
    t.Set([-2.100,5.0,-2.9])
    s = t.GetAsBytes()
    print(s)
    t.SetFromBytes(s)
    print(t.Get())