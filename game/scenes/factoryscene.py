from engine.datatypes.spritesheet import SpriteSheet
from engine.scenes.levelscene import LevelScene
from engine.systems import renderer


class TinyFactoryScene(LevelScene):
    def __init__(self):
        super().__init__("game\\tiled\\factorymap.tmj", SpriteSheet("game\\art\\tilset.png",16), None)
        self.GetSystemByClass(renderer.RenderingSystem).renderScale = 2