import pygame

from engine.ecs import EntitySystem, Scene
from engine.engine import Input
from engine.systems.renderer import RenderingSystem


class TestGameSystem(EntitySystem):
    def __init__(self):
        super().__init__()
    def Update(self, currentScene: Scene):
        if (Input.KeyPressed(pygame.K_w)):
            RenderingSystem.instance.cameraPosition[1] -= 1
        elif (Input.KeyPressed(pygame.K_s)):
            RenderingSystem.instance.cameraPosition[1] += 1
        if (Input.KeyPressed(pygame.K_a)):
            RenderingSystem.instance.cameraPosition[0] -= 1
        elif (Input.KeyPressed(pygame.K_d)):
            RenderingSystem.instance.cameraPosition[0] += 1
        if (Input.KeyDown(pygame.K_SPACE)):
            if(RenderingSystem.instance.debug == True):
                RenderingSystem.instance.debug = False
            else:
                RenderingSystem.instance.debug = True