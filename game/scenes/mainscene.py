from engine.datatypes.spritesheet import SpriteSheet
from engine.scenes.levelscene import LevelScene
from engine.systems.physics import PhysicsSystem
from game.prefabs.PlayerPrefab import CreatePlayer
from game.systems.playersystem import PlayerSystem


class MainScene(LevelScene):
    def __init__(self):
        super().__init__("game/art/tiled/mainlevel.tmj", SpriteSheet("game/art/0x72_DungeonTilesetII_v1.7.png",16), None)
        self.systems.append(PlayerSystem())
        self.systems.append(PhysicsSystem())
    def LevelStart(self):
        CreatePlayer(self)