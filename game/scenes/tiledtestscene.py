import pygame

from engine import ecs
from engine.ecs import Entity, Scene
from engine.systems import renderer, physics
import random

from engine.systems.physics import PhysicsComponent
from engine.systems.renderer import TilemapRenderer, SpriteRenderer, AnimatedSprite
from engine.tools.spritesheet import SpriteSheet
from engine.tools.tiled import TiledGetTileMapFromTiledJSON, TiledGetObjectsFromTiledJSON, TiledGetObjectByName
from game import prefabs
from game.assets import worldTileset
from game.systems import playersystem
from game.systems.NPCSystem import NPCComponent, NPCSystem


class TiledTestScene(Scene):
    def __init__(self):
        super().__init__()
        self.systems = [renderer.RenderingSystem(),playersystem.PlayerSystem(),physics.PhysicsSystem(),NPCSystem()]
    def Init(self):
        self.Clear()
        mapEntity = self.CreateEntity(name="Map Entity", position=[0,0], components=[TilemapRenderer(TiledGetTileMapFromTiledJSON("game/art/tiled/testmap1.tmj", "Tile Layer 1", worldTileset))])
        mapEntity.GetComponent(TilemapRenderer).tileMap.tileSize = 16
        levelObjects = TiledGetObjectsFromTiledJSON("game/art/tiled/testmap1.tmj", "Object Layer 1")

        playerSpawn = TiledGetObjectByName(levelObjects,"SPAWN")

        p1 = prefabs.CreatePlayer(self)
        p1.GetComponent(PhysicsComponent).collidesWithLayers = []
        p1.position = playerSpawn["position"]#[playerSpawn["x"]-16*50,playerSpawn["y"]-16*15]

        skeletonSpawn = TiledGetObjectByName(levelObjects, "SKELETON")
        skeleton = prefabs.CreateSkeleton(self,0)
        skeleton.position = skeletonSpawn["position"]#[skeletonSpawn["x"]-16*50,skeletonSpawn["y"]-16*15]

        super().Init()