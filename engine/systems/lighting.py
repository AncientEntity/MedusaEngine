from pygame import BLEND_RGBA_SUB, BLEND_RGB_ADD, BLEND_RGBA_ADD

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
        self.drawOrder = 1000

        self._rendering : RenderingSystem = None

        self._worldLightEntity : Entity = None
        self._worldLightSprite : Sprite = None

        self.minAlphaSurface : pygame.Surface = None



    def Update(self,currentScene : Scene):

        rawSurface : pygame.Surface = self._worldLightSprite.GetSprite()

        # Reset the light sprite to being fully black with the world brightness alpha.
        rawSurface.fill((0, 0, 0, self.worldBrightness))

        # Apply light brightness (just the alpha for nwo)
        light : LightComponent
        for light in currentScene.components[LightComponent]:
            if not self._rendering.IsOnScreenRect(pygame.Rect(light.parentEntity.position[0]-light.radius,
                                                              light.parentEntity.position[1]-light.radius,
                                                              light.radius*2, light.radius*2)):
                continue # Light not on screen.

            if light.brightness != light.cachedBrightness or light.radius != light.cachedRadius or \
                    light.color != light.cachedColor:
                self.CreateLightSprite(light)

            surfacePosition = self._rendering.WorldToScreenPosition(light.parentEntity.position)

            # We first subtract the alpha out
            rawSurface.blit(light.cachedLightSurface, (surfacePosition[0] - light.radius,
                                                       surfacePosition[1] - light.radius),
                            special_flags=BLEND_RGBA_SUB)

        # Now set a minimum alpha. For now self.minAlphaSurface is (0,0,0,255-brightness) (see it's creation just in case)
        rawSurface.blit(self.minAlphaSurface,(0,0), special_flags=pygame.BLEND_RGBA_MAX)

        # Now we apply color.
        for light in currentScene.components[LightComponent]:
            if not self._rendering.IsOnScreenRect(pygame.Rect(light.parentEntity.position[0]-light.radius,
                                                              light.parentEntity.position[1]-light.radius,
                                                              light.radius*2, light.radius*2)):
                continue # Light not on screen

            surfacePosition = self._rendering.WorldToScreenPosition(light.parentEntity.position)

            rawSurface.blit(light.cachedColorSurface, (surfacePosition[0] - light.radius,
                                                       surfacePosition[1] - light.radius),
                            special_flags=BLEND_RGBA_ADD)



    def OnEnable(self, currentScene : Scene):
        self._rendering = currentScene.GetSystemByClass(RenderingSystem)
        if not self._rendering:
            Log("No rendering system found", LOG_ERRORS)

        self.InitializeWorldLightEntity(currentScene)

    def InitializeWorldLightEntity(self, currentScene : Scene):
        lightSurface = pygame.Surface(self._rendering._scaledScreenSize, pygame.SRCALPHA, 32)
        lightSurface.convert_alpha()
        lightSurface.fill((0, 0, 0, self.worldBrightness))
        self.minAlphaSurface = pygame.Surface(self._rendering._scaledScreenSize, pygame.SRCALPHA, 32)
        self.minAlphaSurface.fill((0, 0, 0, 255 - self.worldBrightness))


        self._worldLightSprite = Sprite(lightSurface)
        self._worldLightEntity = currentScene.CreateEntity("EngineLightMask", (0, 0), components=[
            SpriteRenderer(self._worldLightSprite, self.drawOrder, True)])

    def CreateLightSprite(self, light : LightComponent):
        lightSurface = pygame.Surface((light.radius*2,light.radius*2), pygame.SRCALPHA, 32)
        lightSurface.convert_alpha()
        colorSurface = pygame.Surface((light.radius*2,light.radius*2), pygame.SRCALPHA, 32)
        colorSurface.convert_alpha()

        for i in range(light.radius):
            inverse = Clamp((1.0 - (i / light.radius)) * light.brightness,0.0,1.0)
            brightness = self.worldBrightness * inverse
            color = (light.color[0] * inverse,
                     light.color[1] * inverse,
                     light.color[2] * inverse,
                     Clamp(brightness,0 , 255))
            pygame.draw.circle(lightSurface, (0,0,0,color[3]), (light.radius,light.radius), i, width=2)
            pygame.draw.circle(colorSurface, (color[0],color[1],color[2],brightness//25), (light.radius,light.radius), i, width=2)

        light.cachedLightSurface = lightSurface
        light.cachedColorSurface = colorSurface
        light.cachedBrightness = light.brightness
        light.cachedRadius = light.radius
        light.cachedColor = light.color

    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        pass
    def OnDeleteComponent(self, component : Component): #Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        pass