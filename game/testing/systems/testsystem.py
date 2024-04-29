import pygame

from engine.ecs import EntitySystem, Scene
from engine.engine import Input


class TestGameSystem(EntitySystem):
    def __init__(self):
        super().__init__()
    def Update(self, currentScene: Scene):
        if(Input.KeyPressed(pygame.K_w)):
            print("T")