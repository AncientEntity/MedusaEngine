import pygame

from data import ecs
from data.systems import renderer
from data.systems.renderer import SpriteRenderer
import random

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
tileMapComp.tileMap = renderer.Tilemap([25,25])
tileMapComp.tileMap.tileSize = 50
tileMapComp.tileMap.tileSet[0] = pygame.image.load("data/art/testsquare.png")
for x in range(25):
    for y in range(25):
        if(random.randint(0,100) <= 50):
            tileMapComp.tileMap.SetTile(0,x,y)
TestScene.AddComponent(tileMapComp)