import asyncio
import copy

import pygame
import data.ecs as ecs
from data.constants import KEYDOWN, KEYUP, KEYPRESSED, KEYINACTIVE
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

        self._inputStates = {}
    async def Start(self):
        Log("Game Starting",LOG_ALL)
        self.Init()

        self.running = True
        self._lastTickStart = time.time()
        while self.running:
            self.deltaTime = time.time() - self._lastTickStart
            self._lastTickStart = time.time()

            #Game Loop
            self.InputTick()
            self._currentScene.Update()

            await asyncio.sleep(0)
    def Init(self):
        Log("Game Initializing",LOG_ALL)
        pygame.init()
        pygame.mixer.init()
        self.display = pygame.display.set_mode((600,600))
        self.LoadScene(self._currentScene)

        Log("Game Initialized",LOG_ALL)

    def InputTick(self):

        #Go through and mark any KEYDOWN keys as KEYPRESSED and KEYUP keys as inactive.
        for key in self._inputStates.keys():
            if(self._inputStates[key] == KEYDOWN):
                self._inputStates[key] = KEYPRESSED
            elif(self._inputStates[key] == KEYUP):
                self._inputStates[key] = KEYINACTIVE

        #Check all the new pygame events for quitting and keys.
        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                self.Quit()
            elif(event.type == pygame.KEYDOWN):
                self._inputStates[event.key] = KEYDOWN
            elif(event.type == pygame.KEYUP):
                self._inputStates[event.key] = KEYUP
    def IsKeyState(self,key : int, targetState : int) -> bool:
        if(key in self._inputStates):
            return self._inputStates[key] == targetState
        else:
            return False #Key Inactive/never recorded.
    def KeyPressed(self,key : int) -> bool:
        return self.IsKeyState(key,KEYPRESSED) or self.IsKeyState(key,KEYDOWN)
    def KeyDown(self,key : int) -> bool:
        return self.IsKeyState(key,KEYDOWN)
    def KeyUp(self,key : int) -> bool:
        return self.IsKeyState(key,KEYUP)

    def LoadScene(self, scene):
        self._currentScene = copy.copy(scene)
        self._currentScene.game = self
        self._currentScene.Init()
    def Quit(self):
        Log("Game Quitting",LOG_ALL)
        exit(0)