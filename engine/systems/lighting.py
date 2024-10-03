from pygame import BLEND_RGBA_SUB, BLEND_RGB_ADD

from engine.components.rendering.lightcomponent import LightComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.sprites import Sprite
from engine.ecs import EntitySystem, Scene, Component, Entity
import pygame

from engine.logging import Log, LOG_ERRORS
from engine.systems.renderer import RenderingSystem
from engine.tools.math import Clamp


class LightingSystem(EntitySystem):
    def __init__(self):
        super().__init__([LightComponent])

        self.worldBrightness = 200 # The default alpha of the world's light surface. (0 - 255)

        self._rendering : RenderingSystem = None

        self._worldLightEntity : Entity = None
        self._worldLightSprite : Sprite = None



    def Update(self,currentScene : Scene):

        rawSurface : pygame.Surface = self._worldLightSprite.GetSprite()

        # Reset the light sprite to being fully black with the world brightness alpha.
        rawSurface.fill((0, 0, 0, self.worldBrightness))

        light : LightComponent
        for light in currentScene.components[LightComponent]:
            halfRadius = light.radius // 2
            if not self._rendering.IsOnScreenRect(pygame.Rect(light.parentEntity.position[0]-halfRadius,
                                                              light.parentEntity.position[1]-halfRadius,
                                                              light.radius, light.radius)):
                continue # Light not on screen.

            if light.brightness != light.cachedBrightness or light.radius != light.cachedRadius:
                self.CreateLightSprite(light)

            surfacePosition = self._rendering.WorldToScreenPosition(light.parentEntity.position)

            # We first subtract the alpha out, then add just the RGB
            rawSurface.blit(light.cachedLight,(surfacePosition[0]-light.radius,
                                                surfacePosition[1]-light.radius),
                            special_flags=BLEND_RGBA_SUB)
            # Notice this is the BLEND_RGB_ADD not BLEND_RGBA_ADD flag...
            rawSurface.blit(light.cachedLight,(surfacePosition[0]-light.radius,
                                                surfacePosition[1]-light.radius),
                            special_flags=BLEND_RGB_ADD)


    def OnEnable(self, currentScene : Scene):
        self._rendering = currentScene.GetSystemByClass(RenderingSystem)
        if not self._rendering:
            Log("No rendering system found", LOG_ERRORS)

        self.InitializeWorldLightEntity(currentScene)

    def InitializeWorldLightEntity(self, currentScene : Scene):
        lightSurface = pygame.Surface(self._rendering._scaledScreenSize, pygame.SRCALPHA, 32)
        lightSurface.convert_alpha()
        self._worldLightSprite = Sprite(lightSurface)
        self._worldLightEntity = currentScene.CreateEntity("EngineLightMask", (0, 0), components=[
            SpriteRenderer(self._worldLightSprite, 50000, True)])

    def CreateLightSprite(self, light : LightComponent):
        lightSurface = pygame.Surface((light.radius*2,light.radius*2), pygame.SRCALPHA, 32)
        lightSurface.convert_alpha()

        for i in range(light.radius):
            brightness = 255 - i * 10
            inverse = 1.0 - (i / light.radius)
            color = (light.color[0] * inverse,
                     light.color[1] * inverse,
                     light.color[2] * inverse,
                     Clamp(brightness,0 , 255))
            pygame.draw.circle(lightSurface, color, (light.radius,light.radius), i, width=2)

        light.cachedLight = lightSurface
        light.cachedBrightness = light.brightness
        light.cachedRadius = light.radius

    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        pass
    def OnDeleteComponent(self, component : Component): #Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        pass