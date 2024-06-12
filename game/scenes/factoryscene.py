import pygame.font

from engine.components.rendering.textrenderer import TextRenderer
from engine.datatypes.spritesheet import SpriteSheet
from engine.scenes.levelscene import LevelScene
from engine.systems import renderer
from game.systems.uisystem import UISystem


class TinyFactoryScene(LevelScene):
    def __init__(self):
        super().__init__("game/tiled/factorymap.tmj", SpriteSheet("game/art/tilset.png",16), None)
        self.systems.append(UISystem())
        self.GetSystemByClass(renderer.RenderingSystem).renderScale = 2