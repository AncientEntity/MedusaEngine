import struct
import time

from engine.networking.variables.networkvarvector import NetworkVarVector, WrappedList
from engine.tools.math import Distance, MoveTowards

class NetworkVarVectorInterpolate(NetworkVarVector):
    def __init__(self, defaultValue=[0,0]):
        super().__init__(defaultValue)

        self.interpolateSpeed = 5
        self.interpolateMaxDistance = 500
        self._interpolatePosition = defaultValue[:]
        self._lastInterpolateTime = time.time()

        self.minByteChangeDifference = 100

    def Set(self, value : list, modified=True):
        super().Set(value, modified)
        distance = Distance(self._interpolatePosition, self.value)
        if distance >= self.interpolateMaxDistance or self.hasAuthority:
            self._interpolatePosition = self.value[:]

    def Get(self):
        if self.hasAuthority:
            return WrappedList(self.value,self.value, self)
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