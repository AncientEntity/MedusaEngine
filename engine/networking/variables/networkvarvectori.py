import struct
import time

from engine.networking.variables.networkvarvector import NetworkVarVector, WrappedList
from engine.tools.math import Distance, MoveTowards

class NetworkVarVectorInterpolate(NetworkVarVector):
    def __init__(self, defaultValue=[0,0]):
        super().__init__(defaultValue)

        self.interpolateSpeed = 0.45
        self.interpolateMaxDistance = 50
        self._interpolatePosition = defaultValue[:]
        self._lastInterpolateTime = time.time()

        self.minByteChangeDifference = None

    def Set(self, value : list, modified=True):
        super().Set(value, modified)
        if not isinstance(value, WrappedList): # we might not need this depending on how WrappedList takes in a value...
            self._interpolatePosition = self.value[:]
        else:
            self._interpolatePosition = self.value[:].interp

    def Get(self):
        if self.hasAuthority:
            return WrappedList(self.value,self.value, self)
        else:
            distance = Distance(self._interpolatePosition, self.value)
            if distance > self.interpolateMaxDistance:
                self._interpolatePosition = self.value[:]
                return self._interpolatePosition

            curTime = time.time()
            if distance <= self.interpolateSpeed: # todo issue seems to be coming from movetowards
                self._interpolatePosition = MoveTowards(self._interpolatePosition, self.value, self.interpolateSpeed*(curTime-self._lastInterpolateTime)*distance**2)
            self._lastInterpolateTime = curTime
            return WrappedList(self._interpolatePosition,self._interpolatePosition, self)

if __name__ == '__main__':
    t = NetworkVarVectorInterpolate()
    t.Set([-2.100,5.0,-2.9])
    s = t.GetAsBytes()
    print(s)
    t.SetFromBytes(s)
    print(t.value)