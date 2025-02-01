import struct
import time

from engine.networking.variables.networkvarvector import NetworkVarVector
from engine.tools.math import Distance, MoveTowards

class WrappedList:
    def __init__(self, list, interp, netVar):
        self.list = list
        self.interp = interp
        self.netVar = netVar
    def __getitem__(self, item):
        if not self.netVar._modified:
            return self.interp[item]
        return self.list[item]
    def __setitem__(self, key, value):
        self.list[key] = value
        self.interp[key] = value
        if self.netVar.hasAuthority:
            self.netVar._modified = True #todo temp

class NetworkVarVectorInterpolate(NetworkVarVector):
    def __init__(self, defaultValue=[0,0]):
        super().__init__(defaultValue)

        self.interpolateSpeed = 5
        self.interpolateMaxDistance = 500
        self._interpolatePosition = defaultValue[:]
        self._lastInterpolateTime = time.time()

    def Set(self, value : list, modified=True):
        super().Set(value, modified)
        distance = Distance(self._interpolatePosition, self.value)
        if distance >= self.interpolateMaxDistance or self.hasAuthority:
            self._interpolatePosition = self.value[:]

    def Get(self):
        if self.hasAuthority:
            return self.value
        else:
            distance = Distance(self._interpolatePosition, self.value)
            if distance > self.interpolateMaxDistance:
                self._interpolatePosition = self.value[:]
                return self._interpolatePosition

            curTime = time.time()
            self._interpolatePosition = MoveTowards(self._interpolatePosition, self.value, self.interpolateSpeed*(curTime-self._lastInterpolateTime)*distance)
            self._lastInterpolateTime = curTime
            return WrappedList(self.value,self._interpolatePosition, self)

if __name__ == '__main__':
    t = NetworkVarVectorInterpolate()
    t.Set([-2.100,5.0,-2.9])
    s = t.GetAsBytes()
    print(s)
    t.SetFromBytes(s)
    print(t.value)