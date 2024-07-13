from engine.datatypes.spritesheet import SpriteSheet
from engine.scenes.levelscene import LevelScene
from engine.systems.renderer import RenderingSystem


class PathfindingScene(LevelScene):
    def __init__(self):
        super().__init__("game/art/tiled/pathfinding.tmj", SpriteSheet("game/art/0x72_DungeonTilesetII_v1.7.png",16), None)
        self.GetSystemByClass(RenderingSystem).renderScale = 1