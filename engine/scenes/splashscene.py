#Engine splash screen scene
import pygame.font

from engine.ecs import Scene, EntitySystem
from engine.systems.renderer import RenderingSystem, SpriteRenderer
from engine.tools.math import Clamp


#This loads the starting scene of the game after X seconds
class EngineSplashScreenLoadNextScene(EntitySystem):
    def __init__(self):
        super().__init__()
        self.timeLeft = 1.8
    def Update(self, currentScene: Scene):
        self.timeLeft -= self.game.deltaTime
        greyColor = Clamp(255 * (self.timeLeft / 2) + 35, 0, 255)
        currentScene.engineNameEntity.GetComponent(SpriteRenderer).sprite.SetColor((greyColor,greyColor,greyColor))
        currentScene.engineIconEntity.GetComponent(SpriteRenderer).sprite.SetColor((greyColor,greyColor,greyColor))

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
    def Init(self):
        super().Init()
        font = pygame.font.SysFont("Arial", 36, True, False)
        engineNameText = font.render("Powered by Medusa Engine", True, (255, 255, 255))
        self.engineNameEntity = self.CreateEntity("Engine Name Text",[0,-200],[SpriteRenderer(engineNameText)])
        self.engineNameEntity.name = "Engine Name Text"

        engineIcon = pygame.image.load("engine/art/logo.png")
        self.engineIconEntity = self.CreateEntity("Engine Icon",[0,0],[SpriteRenderer(engineIcon)])
        self.engineIconEntity.GetComponent(SpriteRenderer).sprite.SetScale((3,3))
        self.engineIconEntity.name = "Engine Icon"

        RenderingSystem.instance.backgroundColor = (0,0,0)

engineSplashScreenScene = EngineSplashScreenScene