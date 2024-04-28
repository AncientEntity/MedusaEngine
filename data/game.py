import asyncio
import copy

import pygame
import data.ecs as ecs
from data.logging import *
import time

from data.scenes.testing.TestScene import TestScene


class Game:
    def __init__(self):
        self._currentScene : ecs.Scene = TestScene
        self.display : pygame.Surface = None
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

            #import random
            #self._currentScene.entities[0].position = [random.randint(0,300),random.randint(0,300)]


            await asyncio.sleep(0)
    def Init(self):
        Log("Game Initializing",LOG_ALL)
        pygame.init()
        pygame.mixer.init()
        self.display = pygame.display.set_mode((600,600))
        self.LoadScene(self._currentScene)

        Log("Game Initialized",LOG_ALL)
    def LoadScene(self, scene):
        self._currentScene = copy.copy(scene)
        self._currentScene.game = self
        self._currentScene.Init()
    def Quit(self):
        Log("Game Quitting",LOG_ALL)
        exit(0)