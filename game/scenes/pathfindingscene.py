from engine.datatypes.spritesheet import SpriteSheet
from engine.scenes.levelscene import LevelScene
from engine.systems.renderer import RenderingSystem
from game.systems.TestSystem import TestSystem


class PathfindingScene(LevelScene):
    def __init__(self):
        super().__init__("game/art/tiled/pathfindinglevel.tmj", SpriteSheet("game/art/0x72_DungeonTilesetII_v1.7.png",16), None)
        self.GetSystemByClass(RenderingSystem).renderScale = 1
        self.systems.append(TestSystem())