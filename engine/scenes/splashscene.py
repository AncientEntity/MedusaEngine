#Engine splash screen scene
import pygame.font

from engine.ecs import Scene, Entity, EntitySystem
from engine.systems.renderer import RendererSystem, SpriteRenderer

#This loads the starting scene of the game after X seconds
class EngineSplashScreenLoadNextScene(EntitySystem):
    def __init__(self):
        super().__init__()
        self.timeLeft = 3
    def Update(self, currentScene: Scene):
        self.timeLeft -= self.game.deltaTime
        if(self.timeLeft <= 0):
            self.game.LoadScene(self.game._game.startingScene)

class EngineSplashScreenScene(Scene):
    def __init__(self):
        super().__init__()
        self.renderEngine = RendererSystem()
        self.renderEngine.renderScale = 1
        self.systems.append(self.renderEngine)
        self.systems.append(EngineSplashScreenLoadNextScene())
    def Init(self):
        super().Init()
        font = pygame.font.SysFont("Arial", 36, True, False)
        engineNameText = font.render("Powered by Catalyst Engine", True, (0, 0, 0))
        engineNameEntity = Entity()
        engineNameEntity.position = [self.game.display.get_width()//2,self.game.display.get_height()//6]
        engineNameEntity.name = "Engine Name Text"
        self.entities.append(engineNameEntity)
        self.AddComponent(SpriteRenderer(engineNameEntity,engineNameText)) #Eventually we'll want a TextRenderer instead of using a SpriteRenderer.

        engineIcon = pygame.image.load("engine/art/logo.png")
        engineIcon = pygame.transform.scale(engineIcon,(engineIcon.get_width()*(self.game.display.get_width()//300),engineIcon.get_height()*(self.game.display.get_height()//300)))
        engineIconEntity = Entity()
        engineIconEntity.position = [self.game.display.get_width()//2,self.game.display.get_height()//2]
        engineIconEntity.name = "Engine Icon"
        self.entities.append(engineIconEntity)
        self.AddComponent(SpriteRenderer(engineIconEntity,engineIcon))

engineSplashScreenScene = EngineSplashScreenScene()