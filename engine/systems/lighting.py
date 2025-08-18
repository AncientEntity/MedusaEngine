from pygame import BLEND_RGBA_SUB, BLEND_RGB_ADD, BLEND_RGBA_ADD

from engine.components.rendering.lightcomponent import LightComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.sprites import Sprite
from engine.ecs import EntitySystem, Scene, Component, Entity
import pygame

from engine.engine import Input
from engine.logging import Log, LOG_ERRORS, LOG_INFO
from engine.scenes.levelscene import LevelScene
from engine.systems.renderer import RenderingSystem
from engine.tools.math import Clamp, Magnitude


class LightingSystem(EntitySystem):
    def __init__(self):
        super().__init__([LightComponent])
        self.removeOnHeadless = True

        self.worldBrightness = 200 # The default alpha of the world's light surface. (0 - 255)
        self.drawOrder = 1000

        self._rendering : RenderingSystem = None

        self._worldLightEntity : Entity = None
        self._worldLightSprite : Sprite = None



    def Update(self,currentScene : Scene):

        rawSurface : pygame.Surface = self._worldLightSprite.GetSprite()

        # todo remove eventually
        #if Input.KeyDown(pygame.K_l):
        #    if self._worldLightSprite.GetSprite():
        #        self._worldLightSprite.sprite = None
        #    else:
        #        lightSurface = pygame.Surface(self._rendering._scaledScreenSize, pygame.SRCALPHA, 32)
        #        lightSurface.convert_alpha()
        #        self._worldLightSprite.sprite = lightSurface
        #if not rawSurface:
        #    return

        # Reset the light sprite to being fully black with the world brightness alpha.
        rawSurface.fill((0, 0, 0, self.worldBrightness))

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

            # We first subtract the alpha out, then add just the RGB
            rawSurface.blit(light.cachedLightSurface, (surfacePosition[0] - light.radius,
                                                       surfacePosition[1] - light.radius),
                            special_flags=BLEND_RGBA_SUB)
            # Notice this is the BLEND_RGB_ADD not BLEND_RGBA_ADD flag...
            rawSurface.blit(light.cachedColorSurface, (surfacePosition[0] - light.radius,
                                                       surfacePosition[1] - light.radius),
                            special_flags=BLEND_RGBA_ADD)


    def OnEnable(self, currentScene : Scene):
        self._rendering : RenderingSystem = currentScene.GetSystemByClass(RenderingSystem)
        if not self._rendering:
            Log("No rendering system found", LOG_ERRORS)

        self._rendering.onScreenUpdated.append(lambda : self.InitializeWorldLightEntity(currentScene))
        self.InitializeWorldLightEntity(currentScene)

    def InitializeWorldLightEntity(self, currentScene : Scene):
        lightSurface = pygame.Surface(self._rendering._scaledScreenSize, pygame.SRCALPHA, 32)
        lightSurface.convert_alpha()
        lightSurface.fill((0, 0, 0, self.worldBrightness))

        self._worldLightSprite = Sprite(lightSurface)
        if not self._worldLightEntity:
            self._worldLightEntity = currentScene.CreateEntity("EngineLightMask", (0, 0), components=[
                SpriteRenderer(self._worldLightSprite, self.drawOrder, True)])
        else:
            self._worldLightEntity.GetComponent(SpriteRenderer).SetSprite(self._worldLightSprite)

        Log(f"InitializeWorldLightEntity with surface size {self._rendering._scaledScreenSize}",LOG_INFO)


    def CreateLightSprite(self, light : LightComponent):
        lightSurface = pygame.Surface((light.radius*2,light.radius*2), pygame.SRCALPHA, 32)
        lightSurface.convert_alpha()
        colorSurface = pygame.Surface((light.radius*2,light.radius*2), pygame.SRCALPHA, 32)
        colorSurface.convert_alpha()

        for i in range(light.radius):
            inverse = Clamp((1.0 - (i / light.radius)) * light.brightness,0,1)
            brightness = 255 * inverse
            lightColor = (light.color[0] * inverse,
                     light.color[1] * inverse,
                     light.color[2] * inverse,
                     Clamp(brightness,0 , 255))
            tintColor = (light.color[0] * inverse,
                     light.color[1] * inverse,
                     light.color[2] * inverse,
                     # 441.67295593006371 is the max possible magnitude (Magnitude((255,255,255))
                     Clamp(Magnitude(light.color) / 441.67295593006371 * 255 * inverse,0 , 255))
            pygame.draw.circle(lightSurface, lightColor, (light.radius,light.radius), i, width=2)
            pygame.draw.circle(colorSurface, tintColor, (light.radius,light.radius), i, width=2)

        light.cachedLightSurface = lightSurface
        light.cachedColorSurface = colorSurface
        light.cachedBrightness = light.brightness
        light.cachedRadius = light.radius
        light.cachedColor = light.color

    def CreateLightsFromLevelScene(self, levelScene : LevelScene):
        for lightData in levelScene.GetTiledObjectsByName("light"):
            if "properties" not in lightData:
                return

            properties = lightData["properties"]
            brightness = 1
            radius = 30
            color = [0, 0, 0]
            for property in properties:
                if property["name"] == "brightness":
                    brightness = property["value"]
                elif property["name"] == "radius":
                    radius = property["value"]
                elif property["name"] == "color":
                    hexColor = property["value"]
                    color[0] = int(hexColor[3:5], 16)
                    color[1] = int(hexColor[5:7], 16)
                    color[2] = int(hexColor[7:9], 16)

            lightComponent = LightComponent(brightness, radius, color)
            levelScene.CreateEntity("GeneratedLevelSceneLight", lightData["position"][:],
                                    components=[lightComponent])

    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        pass
    def OnDeleteComponent(self, component : Component): #Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        pass