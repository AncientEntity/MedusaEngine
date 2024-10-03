from engine.ecs import Component
import pygame

class LightComponent(Component):
    def __init__(self):
        super().__init__()

        self.brightness = 30
        self.radius = 30
        import random
        self.color = (random.randint(0,100),random.randint(0,100),random.randint(0,100))

        self.cachedBrightness = None
        self.cachedRadius = None
        self.cachedLight : pygame.Surface = None