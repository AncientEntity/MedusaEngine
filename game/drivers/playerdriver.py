import pygame

from engine.ecs import Scene
from engine.engine import Input
from engine.systems.renderer import RenderingSystem
from game.components.actorcomponent import ActorComponent
from game.drivers.driverbase import DriverBase


class PlayerDriver(DriverBase):
    def __init__(self):
        super().__init__()
        self.inputs["up"] = lambda : Input.KeyPressed(pygame.K_w)
        self.inputs["down"] = lambda : Input.KeyPressed(pygame.K_s)
        self.inputs["left"] = lambda : Input.KeyPressed(pygame.K_a)
        self.inputs["right"] = lambda : Input.KeyPressed(pygame.K_d)
        self.inputs["attack1"] = lambda : Input.MouseButtonPressed(0)
        self.inputs["reload"] = lambda : Input.KeyDown(pygame.K_r)
        self.inputs["dash"] = lambda : Input.KeyPressed(pygame.K_LSHIFT)
    def Update(self, actor : ActorComponent, currentScene : Scene):
        self.targetPosition = currentScene.GetSystemByClass(RenderingSystem).worldMousePosition #todo nope