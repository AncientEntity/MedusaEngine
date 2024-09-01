from engine.datatypes.spritesheet import SpriteSheet
from engine.scenes.levelscene import LevelScene
from engine.systems.physics import PhysicsSystem
from engine.systems.renderer import RenderingSystem
from game.prefabs.ItemPrefabs import CreateWoodenBowPrefab
from game.prefabs.enemies.LichEyePrefab import CreateLichEyePrefab
from game.prefabs.PlayerPrefab import CreatePlayer
from game.systems.actorsystem import ActorSystem
from game.systems.playersystem import PlayerSystem
import random

from game.systems.weaponsystem import WeaponSystem


class MainScene(LevelScene):
    def __init__(self):
        super().__init__("game/art/tiled/mainlevel.tmj", SpriteSheet("game/art/0x72_DungeonTilesetII_v1.7.png",16), None)
        self.systems.append(PlayerSystem())
        self.systems.append(ActorSystem())
        self.systems.append(PhysicsSystem())
        self.systems.append(WeaponSystem())
        #self.systems.append(GroundSystem())
        self.GetSystemByClass(RenderingSystem).backgroundColor = (40,25,40)
    def LevelStart(self):
        player = CreatePlayer(self)
        self.GetSystemByClass(ActorSystem).cameraTarget = player

        CreateWoodenBowPrefab(self)
        #CreateSlingshotPrefab(self)

        #g = CreateFloatingSwordPrefab(self)
        #g.position = [100, 110]

        #for i in range(5):
        #    eP = CreatePlayer(self)
        #    eP.GetComponent(ActorComponent).driver = TestAIDriver()
        #    eP.position = [random.randint(-200,200),random.randint(-200,200)]
        for i in range(5):
            #if random.randint(0,100) <= 25:
            #    g = CreateFloatingSwordPrefab(self)
            #else:
            #    g = CreateGoblinPrefab(self)
            g = CreateLichEyePrefab(self)
            g.position = [random.randint(-200, 200), random.randint(-200, 200)]