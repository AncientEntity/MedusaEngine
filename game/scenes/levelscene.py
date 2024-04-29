import pygame

from engine import ecs
from engine.ecs import Entity, Scene
from engine.systems import renderer, physics
import random

from engine.systems.renderer import TilemapRenderer, SpriteRenderer, AnimatedSprite
from engine.tools.spritesheet import SpriteSheet
from game import prefabs
from game.assets import dungeonTileSet
from game.systems import playersystem
from game.systems.NPCSystem import NPCComponent

class LevelScene(Scene):
    def __init__(self):
        super().__init__()
        self.systems = [renderer.RenderingSystem(),playersystem.PlayerSystem(),physics.PhysicsSystem()]
    def Init(self):
        self.Clear()
        mapEntity = self.CreateEntity(name="Map Entity",position=[0,0],components=[TilemapRenderer(renderer.Tilemap([100,100]))])
        mapEntity.GetComponent(TilemapRenderer).tileMap.tileSize = 16
        mapEntity.GetComponent(TilemapRenderer).tileMap.SetTileSetFromSpriteSheet(dungeonTileSet)
        for x in range(100):
            for y in range(100):
                mapEntity.GetComponent(TilemapRenderer).tileMap.SetTile("floor_" + str(random.randint(1, 8)), x, y)
        for i in range(100):
            prefabs.CreateSkeleton(self)

        prefabs.CreatePlayer(self)

        super().Init()