import asyncio
import copy

import pygame
import data.ecs as ecs
from data.logging import *
import time

from data.systems import renderer
from data.systems.renderer import SpriteRenderer


class Game:
    def __init__(self):
        self._currentScene : ecs.Scene = None
        self.display = None
        self.running = False
        self._lastTickStart = 0
        self.deltaTime = 0
    async def Start(self):
        Log("Game Starting",LOG_ALL)
        self.Init()
        self.running = True
        self._lastTickStart = time.time()
        while self.running:
            self.deltaTime = time.time() - self._lastTickStart
            self._lastTickStart = time.time()
            self._currentScene.Update()

            import random
            self._currentScene.entities[0].position = [random.randint(0,300),random.randint(0,300)]


            await asyncio.sleep(0)
    def Init(self):
        Log("Game Initializing",LOG_ALL)
        pygame.init()
        pygame.mixer.init()
        self.display = pygame.display.set_mode((600,600))

        TestScene = ecs.Scene(self)
        TestScene.systems.append(renderer.RendererSystem())
        ent = ecs.Entity()
        TestScene.entities.append(ent)
        ent.position = [500,500]
        t = SpriteRenderer(ent,pygame.image.load("data/art/testplayer.png"))
        TestScene.AddComponent(t)
        self.SwapScene(TestScene)

        Log("Game Initialized",LOG_ALL)
    def SwapScene(self,scene):
        self._currentScene = copy.copy(scene)
        self._currentScene.Init()
    def Quit(self):
        Log("Game Quitting",LOG_ALL)
        exit(0)