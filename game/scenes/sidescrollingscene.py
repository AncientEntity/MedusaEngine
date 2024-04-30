import pygame

from engine import ecs
from engine.ecs import Entity, Scene
from engine.systems import renderer, physics
import random

from engine.systems.physics import PhysicsComponent
from engine.systems.renderer import TilemapRenderer, SpriteRenderer, AnimatedSprite
from engine.tools.spritesheet import SpriteSheet
from game import prefabs
from game.assets import dungeonTileSet
from game.systems import playersystem
from game.systems.NPCSystem import NPCComponent
from game.systems.playersystem import PlayerComponent


class SideScrollingScene(Scene):
    def __init__(self):
        super().__init__()
        self.systems = [renderer.RenderingSystem(),playersystem.PlayerSystem(),physics.PhysicsSystem()]
    def Init(self):
        self.Clear()
        mapEntity = self.CreateEntity(name="Map Entity",position=[0,0],components=[TilemapRenderer(renderer.Tilemap([10,11]))])
        mapEntity.GetComponent(TilemapRenderer).tileMap.tileSize = 16
        mapEntity.GetComponent(TilemapRenderer).tileMap.SetTileSetFromSpriteSheet(dungeonTileSet)
        mapEntity.GetComponent(TilemapRenderer).tileMap.tileSet['wall_left'].hasCollision = True
        for x in range(10):
            for y in range(11):
                if(y == 9 or random.randint(0,100) <= 15):
                    mapEntity.GetComponent(TilemapRenderer).tileMap.SetTile("wall_left", x, y)
                else:
                    mapEntity.GetComponent(TilemapRenderer).tileMap.SetTile("floor_" + str(random.randint(1, 8)), x, y)
        #for i in range(100):
        #    prefabs.CreateSkeleton(self,i)

        p1 = prefabs.CreatePlayer(self)
        p2 = prefabs.CreatePlayer(self)
        p2.GetComponent(PlayerComponent).controls = {'up' : pygame.K_UP, 'down' : pygame.K_DOWN, 'left' : pygame.K_LEFT, 'right' : pygame.K_RIGHT}

        super().Init()