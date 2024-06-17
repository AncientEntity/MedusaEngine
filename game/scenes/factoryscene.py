import pygame.font

from engine.components.rendering.textrenderer import TextRenderer
from engine.datatypes.spritesheet import SpriteSheet
from engine.scenes.levelscene import LevelScene
from engine.systems import renderer
from engine.systems.physics import PhysicsSystem
from engine.systems.ui import UISystem
from game.constants import worldSpriteSheet
from game.prefabs.Generator import CreateGenerator
from game.systems.generatorsystem import GeneratorSystem
from game.systems.itemsystem import ItemSystem
from game.systems.gamesystem import GameSystem


class TinyFactoryScene(LevelScene):
    def __init__(self):
        super().__init__("game/tiled/factorymap.tmj", worldSpriteSheet, None)
        self.systems.append(PhysicsSystem())
        self.systems.append(GameSystem())
        self.systems.append(ItemSystem())
        self.systems.append(GeneratorSystem())
        self.systems.append(UISystem())
        self.GetSystemByClass(renderer.RenderingSystem).renderScale = 2
    def LevelStart(self):
        CreateGenerator(self)