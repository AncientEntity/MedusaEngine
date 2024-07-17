import pygame

from engine.components.rendering.particlecomponent import ParticleEmitterComponent
from engine.datatypes.spritesheet import SpriteSheet
from engine.ecs import Entity
from engine.scenes.levelscene import LevelScene
from engine.systems.physics import PhysicsSystem
from engine.systems.renderer import RenderingSystem
from game.prefabs.PlayerPrefab import CreatePlayer
from game.systems.groundsystem import GroundSystem
from game.systems.playersystem import PlayerSystem
import random


class MainScene(LevelScene):
    def __init__(self):
        super().__init__("game/art/tiled/mainlevel.tmj", SpriteSheet("game/art/0x72_DungeonTilesetII_v1.7.png",16), None)
        self.systems.append(PlayerSystem())
        self.systems.append(PhysicsSystem())
        #self.systems.append(GroundSystem())
        self.GetSystemByClass(RenderingSystem).backgroundColor = (40,25,40)
    def LevelStart(self):
        CreatePlayer(self)