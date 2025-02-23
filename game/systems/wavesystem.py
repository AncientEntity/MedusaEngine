from engine.components.recttransformcomponent import RectTransformComponent
from engine.components.rendering.textrenderer import TextRenderer
from engine.constants import ALIGN_TOPLEFT
from engine.datatypes.font import Font
from engine.datatypes.timedevents import TimedEvent
from engine.ecs import EntitySystem, Scene, Component
import random

from game.prefabs.enemies.FloatingSwordPrefab import CreateFloatingSwordPrefab
from game.prefabs.enemies.GobinPrefab import CreateGoblinPrefab
from game.prefabs.enemies.LichEyePrefab import CreateLichEyePrefab


class WaveSystem(EntitySystem):
    def __init__(self):
        super().__init__([]) #Put target components here

        self.waveEvent : TimedEvent = None

        self.score = 0
        self.scoreText = None

    def Update(self,currentScene : Scene):
        pass
    def OnEnable(self, currentScene : Scene):
        self.waveEvent = TimedEvent(self.SpawnWave,(currentScene,),0,17,None)
        self.StartTimedEvent(self.waveEvent)

        self.CreateScoreEntity(currentScene)
    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        pass
    def OnDestroyComponent(self, component : Component): #Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        pass

    def CreateScoreEntity(self, currentScene : Scene):
        self.scoreText = TextRenderer(f"Score: {self.score}", 16, Font("Arial"))
        self.scoreText.drawOrder = 999999
        self.scoreText.SetColor((255,255,255))
        rectTransform = RectTransformComponent(ALIGN_TOPLEFT, bounds=[0.2,0.1])
        scoreEntity = currentScene.CreateEntity("ScoreText",[0,0],[self.scoreText, rectTransform])

    def AddScore(self, add):
        self.score += add
        self.scoreText.SetText(f"Score: {self.score}")


    def SpawnWave(self, currentScene):
        for i in range(5):
            r = random.randint(0,100)
            if r <= 50:
                g = CreateGoblinPrefab(currentScene)
            elif r <= 80:
                g = CreateFloatingSwordPrefab(currentScene)
            else:
                g = CreateLichEyePrefab(currentScene)
            g.position = random.choice(currentScene.GetTiledObjectsByName("enemySpawn"))["position"][:]