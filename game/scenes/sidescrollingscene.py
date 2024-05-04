import pygame

import random

from engine.components.rendering.tilemaprenderer import Tilemap
from engine.ecs import Scene
from engine.systems import physics, renderer
from engine.systems.renderer import TilemapRenderer
from game import prefabs
from game.assets import dungeonTileSet
from game.systems import playersystem
from game.systems.NPCSystem import NPCSystem
from game.systems.playersystem import PlayerComponent


class SideScrollingScene(Scene):
    def __init__(self):
        super().__init__()
        self.systems = [renderer.RenderingSystem(),playersystem.PlayerSystem(),physics.PhysicsSystem(),NPCSystem()]
    def Init(self):
        self.Clear()
        mapEntity = self.CreateEntity(name="Map Entity",position=[0,0],components=[TilemapRenderer(Tilemap([50,11]))])
        mapEntity.GetComponent(TilemapRenderer).tileMap.tileSize = 16
        mapEntity.GetComponent(TilemapRenderer).tileMap.SetTileSetFromSpriteSheet(dungeonTileSet)
        mapEntity.GetComponent(TilemapRenderer).physicsLayer = 1
        mapEntity.GetComponent(TilemapRenderer).tileMap.tileSet['wall_left'].hasCollision = True
        for x in range(50):
            for y in range(11):
                if(y == 9 or random.randint(0,100) <= 8):
                    mapEntity.GetComponent(TilemapRenderer).tileMap.SetTile("wall_left", x, y)
                else:
                    pass
                    #mapEntity.GetComponent(TilemapRenderer).tileMap.SetTile("floor_" + str(random.randint(1, 8)), x, y)
        for i in range(100):
            if(random.randint(0,100) <= 10):
                prefabs.CreateSkeleton(self).position=[16*i-50,-20]

        p1 = prefabs.CreatePlayer(self)
        p2 = prefabs.CreatePlayer(self)
        p2.GetComponent(PlayerComponent).controls = {'up' : pygame.K_UP, 'down' : pygame.K_DOWN, 'left' : pygame.K_LEFT, 'right' : pygame.K_RIGHT}

        super().Init()