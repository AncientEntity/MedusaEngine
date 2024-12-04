#Engine splash screen scene
import pygame.font

from engine.components.recttransformcomponent import RectTransformComponent
from engine.components.rendering.textrenderer import TextRenderer
from engine.constants import ALIGN_CENTERTOP, ALIGN_CENTERBOTTOM, ALIGN_BOTTOMLEFT
from engine.datatypes.font import Font
from engine.datatypes.sprites import Sprite
from engine.ecs import Scene, EntitySystem
from engine.systems.renderer import RenderingSystem, SpriteRenderer
from engine.systems.ui import UISystem
from engine.tools.math import Clamp


#This loads the starting scene of the game after X seconds
class EngineSplashScreenLoadNextScene(EntitySystem):
    def __init__(self):
        super().__init__()
        self.startingTime = 1.25
        self.timeLeft = self.startingTime

    def Update(self, currentScene: Scene):
        self.timeLeft -= self.game.deltaTime
        alpha = Clamp(255 * (self.timeLeft / self.startingTime * 1.2) + 35, 0, 255)

        currentScene.engineNameText.SetAlpha(alpha)
        currentScene.engineIconSprite.SetAlpha(alpha)

        if(self.timeLeft <= 0):
            self.game.LoadScene(self.game._game.startingScene)

class EngineSplashScreenScene(Scene):
    def __init__(self):
        super().__init__()
        self.renderEngine = RenderingSystem()
        self.renderEngine.renderScale = 1
        self.systems.append(self.renderEngine)
        self.systems.append(EngineSplashScreenLoadNextScene())
        self.systems.append(UISystem())

        self.name = "Medusa Splash Scene"

        self.engineNameText : TextRenderer = None
        self.engineIconSprite : Sprite = None
    def Init(self):

        centerRect = RectTransformComponent(bounds=[0.95,0.6])
        centerRectEntity = self.CreateEntity("CenterRectEntity",[0,0], [centerRect])

        self.engineNameText = TextRenderer("Powered by Medusa Engine", 75, Font("Arial"))
        self.engineNameText.SetColor((255,255,255))
        self.engineNameText.SetFont(None, True)
        self.engineNameEntity = self.CreateEntity("Engine Name Text",[0,-200],[self.engineNameText,
                                               RectTransformComponent(parent=centerRect,bounds=[0.8,0.25],anchor=ALIGN_CENTERTOP)])
        self.engineNameEntity.GetComponent(TextRenderer)
        self.engineNameEntity.name = "Engine Name Text"

        engineIcon = pygame.image.load("engine/art/logo.png")
        self.engineIconEntity = self.CreateEntity("Engine Icon",[0,0],[SpriteRenderer(engineIcon),
                                                  RectTransformComponent(parent=centerRect,bounds=[None,0.6],anchor=ALIGN_CENTERBOTTOM,
                                                                         anchorOffset=[0,0.15])])
        self.engineIconEntity.GetComponent(SpriteRenderer).sprite.SetScale((3,3))
        self.engineIconEntity.name = "Engine Icon"
        self.engineIconSprite = self.engineIconEntity.GetComponent(SpriteRenderer).sprite


        super().Init()

        RenderingSystem.instance.backgroundColor = (0,0,0)

engineSplashScreenScene = EngineSplashScreenScene