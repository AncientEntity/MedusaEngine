import pygame

from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.spritesheet import SpriteSheet
from engine.scenes.levelscene import LevelScene
from engine.systems.physics import PhysicsSystem
from engine.systems.renderer import RenderingSystem
from game import assets
from game.components.actorcomponent import ActorComponent
from game.drivers.testaidriver import TestAIDriver
from game.prefabs.GobinPrefab import CreateGoblinPrefab
from game.prefabs.ItemPrefabs import CreatePistolPrefab
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
        player.GetComponent(SpriteRenderer).sprite = assets.worldTileset[1]
        self.GetSystemByClass(ActorSystem).cameraTarget = player

        CreatePistolPrefab(self)

        for i in range(5):
            eP = CreatePlayer(self)
            eP.GetComponent(ActorComponent).driver = TestAIDriver()
        for i in range(5):
            g = CreateGoblinPrefab(self)