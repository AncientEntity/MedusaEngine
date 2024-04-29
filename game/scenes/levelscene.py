import pygame

from engine import ecs
from engine.ecs import Entity
from engine.systems import renderer
import random

from engine.systems.renderer import TilemapRenderer, SpriteRenderer, AnimatedSprite
from engine.tools.spritesheet import SpriteSheet
from game import prefabs
from game.assets import dungeonTileSet
from game.systems import playersystem
from game.systems.NPCSystem import NPCComponent

LevelScene = ecs.Scene()
LevelScene.systems.append(renderer.RenderingSystem())
LevelScene.systems.append(playersystem.PlayerSystem())

mapEntity = LevelScene.CreateEntity("Map Entity",position=[0,0],components=[TilemapRenderer(renderer.Tilemap([100,100]))])
mapEntity.GetComponent(TilemapRenderer).tileMap.tileSize = 16
mapEntity.GetComponent(TilemapRenderer).tileMap.SetTileSetFromSpriteSheet(dungeonTileSet)

for x in range(100):
    for y in range(100):
        mapEntity.GetComponent(TilemapRenderer).tileMap.SetTile("floor_"+str(random.randint(1,8)),x,y)

for i in range(100):
    prefabs.CreateSkeleton(LevelScene)

prefabs.CreatePlayer(LevelScene)