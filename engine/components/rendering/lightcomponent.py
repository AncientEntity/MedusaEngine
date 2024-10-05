from engine.ecs import Component
import pygame

class LightComponent(Component):
    def __init__(self, brightness=1, radius=30, color=(0,0,0)):
        super().__init__()

        self.brightness = brightness
        self.radius = radius
        import random
        self.color = color#(random.randint(0,200),random.randint(0,200),random.randint(0,200)) #color

        self.cachedBrightness = None
        self.cachedRadius = None
        self.cachedColor = None
        self.cachedLightSurface : pygame.Surface = None
        self.cachedColorSurface : pygame.Surface = None