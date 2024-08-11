import pygame

from engine.components.rendering.particlecomponent import ParticleEmitterComponent
from engine.datatypes.spritesheet import SpriteSheet
from engine.ecs import Entity
from engine.scenes.levelscene import LevelScene
from engine.systems.physics import PhysicsSystem
from engine.systems.renderer import RenderingSystem
from game.prefabs.ItemPrefabs import CreatePistolPrefab
from game.prefabs.MonsterPrefabs import CreateTestMonster
from game.prefabs.PlayerPrefab import CreatePlayer
from game.systems.groundsystem import GroundSystem
from game.systems.monstersystem import MonsterSystem
from game.systems.playersystem import PlayerSystem
import random

from game.systems.weaponsystem import WeaponSystem


class MainScene(LevelScene):
    def __init__(self):
        super().__init__("game/art/tiled/mainlevel.tmj", SpriteSheet("game/art/0x72_DungeonTilesetII_v1.7.png",16), None)
        self.systems.append(PlayerSystem())
        self.systems.append(PhysicsSystem())
        self.systems.append(WeaponSystem())
        self.systems.append(MonsterSystem())
        #self.systems.append(GroundSystem())
        self.GetSystemByClass(RenderingSystem).backgroundColor = (40,25,40)
    def LevelStart(self):
        CreatePlayer(self)
        CreatePistolPrefab(self)
        for i in range(4):
            test = CreateTestMonster(self)
            test.position = [random.randint(-200,200),random.randint(-200,200)]