import pygame

from data import ecs
from data.systems import renderer
from data.systems.renderer import SpriteRenderer
import random
import data.systems.steamworks

from data.tools.spritesheet import SpriteSheet

testSpriteSheet = SpriteSheet("data/art/testtileset.png",16)

TestScene = ecs.Scene()
TestScene.systems.append(renderer.RendererSystem())
for i in range(20):
    ent = ecs.Entity()
    TestScene.entities.append(ent)
    ent.position = [random.randint(0,300),random.randint(0,300)]
    t = SpriteRenderer(ent, pygame.image.load("data/art/testplayer.png"))
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
            tileMapComp.tileMap.SetTile(random.randint(0,10),x,y)
TestScene.AddComponent(tileMapComp)