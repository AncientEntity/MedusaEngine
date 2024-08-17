import pygame
from engine.engine import Input
from engine.tools.math import Clamp
from game.drivers.driverbase import DriverBase
import random

# Test AI Driver, walks around in random directions.
# As such this code isn't really optimized as it's just for quick testing. (so don't judge)

class TestAIDriver(DriverBase):
    def __init__(self):
        super().__init__()

        self.randomDirection = [random.randint(-1,1),random.randint(-1,1)]

        self.inputs["up"] = lambda : self.GetUp()
        self.inputs["down"] = lambda : self.GetDown()
        self.inputs["left"] = lambda : self.GetLeft()
        self.inputs["right"] = lambda : self.GetRight()
        #self.inputs["attack1"] = lambda : Input.MouseButtonPressed(0)
        #self.inputs["dash"] = lambda : Input.KeyPressed(pygame.K_LSHIFT)
    def GetUp(self):
        self.RandomTick()
        return self.randomDirection[1] < 0
    def GetDown(self):
        self.RandomTick()
        return self.randomDirection[1] > 0
    def GetLeft(self):
        self.RandomTick()
        return self.randomDirection[0] < 0
    def GetRight(self):
        self.RandomTick()
        return self.randomDirection[0] > 0
    def RandomTick(self):
        self.randomDirection[0] += random.uniform(-0.1,0.1)
        self.randomDirection[1] += random.uniform(-0.1,0.1)
        self.randomDirection[0] = Clamp(self.randomDirection[0],-1,1)
        self.randomDirection[1] = Clamp(self.randomDirection[1],-1,1)