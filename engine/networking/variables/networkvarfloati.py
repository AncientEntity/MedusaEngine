import time

from engine.networking.variables.networkvarfloat import NetworkVarFloat
from engine.tools.math import Distance, MoveTowards

class NetworkVarFloatInterpolate(NetworkVarFloat):
    def __init__(self, defaultValue=0.0):
        super().__init__(defaultValue)

        self.interpolateSpeed = 50
        self.maxDifference = 25
        self._interpolateValue = defaultValue
        self._lastInterpolateTime = time.time()

    def Set(self, value: list, modified=True):
        if modified:
            super().Set(value, modified)

        self._interpolateValue = value

    def Add(self, value, modified=True):
        if modified:
            super().Add(value, modified)

        self._interpolateValue += value

    def Get(self):
        if self.hasAuthority:
            return self.value
        else:
            diff = (self.value - self._interpolateValue)
            distance = abs(diff)
            if distance > self.maxDifference:
                self._interpolateValue = self.value
                return self.value

            curTime = time.time()
            stepChange = diff * self.interpolateSpeed * (curTime - self._lastInterpolateTime)
            if abs(stepChange) > distance:
                self._interpolateValue = self.value
            else:
                self._interpolateValue += stepChange

            self._lastInterpolateTime = curTime
            return self._interpolateValue