import pygame

from engine import ecs
from engine.systems import renderer
from engine.systems.renderer import SpriteRenderer
import random

from engine.tools.spritesheet import SpriteSheet
from game.testing.systems import testsystem

testSpriteSheet = SpriteSheet("game/testing/art/testing/0x72_DungeonTilesetII_v1.7.png",-1,"game/testing/art/testing/tile_list_v1.7")

TestScene = ecs.Scene()
TestScene.systems.append(renderer.RenderingSystem())
TestScene.systems.append(testsystem.TestGameSystem())
for i in range(20):
    ent = ecs.Entity()
    TestScene.entities.append(ent)
    ent.position = [random.randint(0,300),random.randint(0,300)]
    t = SpriteRenderer(ent, pygame.image.load("game/testing/art/testing/testplayer.png"))
    TestScene.AddComponent(t)

tileEnt = ecs.Entity()
TestScene.entities.append(tileEnt)
tileMapComp = renderer.TilemapRenderer(tileEnt)
tileMapComp.tileMap = renderer.Tilemap([100,25])
tileMapComp.tileMap.tileSize = 16
tileMapComp.tileMap.SetTileSetFromSpriteSheet(testSpriteSheet)

for x in range(100):
    for y in range(25):
        if(random.randint(0,100) <= 90):
            tileMapComp.tileMap.SetTile(random.choice(list(testSpriteSheet.sprites.keys())),x,y)
TestScene.AddComponent(tileMapComp)