import pygame

from engine import ecs
from engine.ecs import Entity
from engine.systems import renderer
import random

from engine.systems.renderer import TilemapRenderer, SpriteRenderer, AnimatedSprite
from engine.tools.spritesheet import SpriteSheet

testSpriteSheet = SpriteSheet("game/testing/art/testing/0x72_DungeonTilesetII_v1.7.png",-1,"game/testing/art/testing/tile_list_v1.7")

LevelScene = ecs.Scene()
LevelScene.systems.append(renderer.RenderingSystem())

mapEntity = LevelScene.CreateEntity("Map Entity",position=[0,0],components=[TilemapRenderer(renderer.Tilemap([100,100]))])
mapEntity.GetComponent(TilemapRenderer).tileMap.tileSize = 16
mapEntity.GetComponent(TilemapRenderer).tileMap.SetTileSetFromSpriteSheet(testSpriteSheet)

def CreatePlayer():
    playerIdleAnim = AnimatedSprite([testSpriteSheet["knight_f_idle_anim_f0"],testSpriteSheet["knight_f_idle_anim_f1"],testSpriteSheet["knight_f_idle_anim_f2"],testSpriteSheet["knight_f_idle_anim_f3"]],10)
    LevelScene.CreateEntity("Player",position=[80,50],components=[SpriteRenderer(playerIdleAnim)])

for x in range(100):
    for y in range(100):
        mapEntity.GetComponent(TilemapRenderer).tileMap.SetTile("floor_"+str(random.randint(1,8)),x,y)

CreatePlayer()