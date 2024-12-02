#Engine splash screen scene
import pygame.font

from engine.components.rendering.textrenderer import TextRenderer
from engine.datatypes.font import Font
from engine.datatypes.sprites import Sprite
from engine.ecs import Scene, EntitySystem
from engine.systems.renderer import RenderingSystem, SpriteRenderer
from engine.tools.math import Clamp


#This loads the starting scene of the game after X seconds
class EngineSplashScreenLoadNextScene(EntitySystem):
    def __init__(self):
        super().__init__()
        self.timeLeft = 1.6

    def Update(self, currentScene: Scene):
        self.timeLeft -= self.game.deltaTime
        alpha = Clamp(255 * (self.timeLeft / 1.2) + 35, 0, 255)

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

        self.name = "Medusa Splash Scene"

        self.engineNameText : TextRenderer = None
        self.engineIconSprite : Sprite = None
    def Init(self):
        self.engineNameText = TextRenderer("Powered by Medusa Engine", 46, Font("Arial"))
        self.engineNameText.SetColor((255,255,255))
        self.engineNameText.SetFont(None, True)
        self.engineNameEntity = self.CreateEntity("Engine Name Text",[0,-200],[self.engineNameText])
        self.engineNameEntity.GetComponent(TextRenderer)
        self.engineNameEntity.name = "Engine Name Text"

        engineIcon = pygame.image.load("engine/art/logo.png")
        self.engineIconEntity = self.CreateEntity("Engine Icon",[0,0],[SpriteRenderer(engineIcon)])
        self.engineIconEntity.GetComponent(SpriteRenderer).sprite.SetScale((3,3))
        self.engineIconEntity.name = "Engine Icon"
        self.engineIconSprite = self.engineIconEntity.GetComponent(SpriteRenderer).sprite

        super().Init()

        RenderingSystem.instance.backgroundColor = (0,0,0)

engineSplashScreenScene = EngineSplashScreenScene