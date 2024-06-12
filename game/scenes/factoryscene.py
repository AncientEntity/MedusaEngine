import pygame.font

from engine.components.rendering.textrenderer import TextRenderer
from engine.datatypes.spritesheet import SpriteSheet
from engine.scenes.levelscene import LevelScene
from engine.systems import renderer
from game.prefabs.Generator import CreateGenerator
from game.systems.generatorsystem import GeneratorSystem
from game.systems.itemsystem import ItemSystem
from game.systems.uisystem import UISystem


class TinyFactoryScene(LevelScene):
    def __init__(self):
        super().__init__("game/tiled/factorymap.tmj", SpriteSheet("game/art/tilset.png",16), None)
        self.systems.append(UISystem())
        self.systems.append(ItemSystem())
        self.systems.append(GeneratorSystem())
        self.GetSystemByClass(renderer.RenderingSystem).renderScale = 2
    def LevelStart(self):
        for i in range(3):
            CreateGenerator(self)