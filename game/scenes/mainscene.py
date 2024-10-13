from engine.components.rendering.lightcomponent import LightComponent
from engine.datatypes.spritesheet import SpriteSheet
from engine.ecs import Scene
from engine.scenes.levelscene import LevelScene
from engine.systems.lighting import LightingSystem
from engine.systems.physics import PhysicsSystem
from engine.systems.renderer import RenderingSystem
from engine.systems.ui import UISystem
from game.prefabs.ItemPrefabs import CreateWoodenBowPrefab, CreateLichFireballPrefab
from game.prefabs.enemies.FloatingSwordPrefab import CreateFloatingSwordPrefab
from game.prefabs.enemies.GobinPrefab import CreateGoblinPrefab
from game.prefabs.enemies.LichEyePrefab import CreateLichEyePrefab
from game.prefabs.PlayerPrefab import CreatePlayer
from game.systems.actorsystem import ActorSystem
from game.systems.playersystem import PlayerSystem
import random

from game.systems.weaponsystem import WeaponSystem


class MainScene(LevelScene):
    def __init__(self):
        super().__init__("game/art/tiled/mainlevel.tmj", SpriteSheet("game/art/0x72_DungeonTilesetII_v1.7.png",16),
                         {"Lava" : self.CreateFire})
        self.systems.append(LightingSystem())
        self.systems.append(PlayerSystem())
        self.systems.append(ActorSystem())
        self.systems.append(PhysicsSystem())
        self.systems.append(WeaponSystem())
        self.systems.append(UISystem())
        #self.systems.append(GroundSystem())
        self.GetSystemByClass(RenderingSystem).backgroundColor = (40,25,40)
    def LevelStart(self):
        player = CreatePlayer(self)
        self.GetSystemByClass(ActorSystem)._cameraTarget = player
        self.GetSystemByClass(LightingSystem).CreateLightsFromLevelScene(self)

        #CreateLichFireballPrefab(self)
        CreateWoodenBowPrefab(self)
        #CreateSlingshotPrefab(self)

        #g = CreateFloatingSwordPrefab(self)
        #g.position = [100, 110]

        #for i in range(5):
        #    eP = CreatePlayer(self)
        #    eP.GetComponent(ActorComponent).driver = TestAIDriver()
        #    eP.position = [random.randint(-200,200),random.randint(-200,200)]
        for i in range(5):
            r = random.randint(0,100)
            if r <= 50:
                g = CreateGoblinPrefab(self)
            elif r <= 80:
                g = CreateFloatingSwordPrefab(self)
            else:
                g = CreateLichEyePrefab(self)
            g.position = [random.randint(-200, 200), random.randint(-200, 200)]

    def CreateFire(self, currentScene : LevelScene):
        light = LightComponent(0.5,42,(100,0,0))
        return currentScene.CreateEntity("FireParticles", (0,0), components=[light])