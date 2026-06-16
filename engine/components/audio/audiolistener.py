from engine.ecs import Component
from engine.tools.math import Clamp
import math


class AudioListener(Component):
    def __init__(self):
        super().__init__()

        self.hearDistance = 700.0

        def defaultFalloff(distance):
            percentage = distance / self.hearDistance
            if percentage <= 0.01:
                return 1
            return Clamp(-math.log(distance/self.hearDistance),0,1)

        self.falloffFunc = defaultFalloff