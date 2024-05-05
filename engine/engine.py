import asyncio
import copy

import pygame
import engine.ecs as ecs
from engine.constants import KEYDOWN, KEYUP, KEYPRESSED, KEYINACTIVE
from engine.game import Game
import time
from sys import exit

from engine.logging import Log, LOG_ALL, LOG_ERRORS, LOG_INFO, LOG_WARNINGS
from engine.scenes import splashscene


class Engine:
    _instance = None
    def __init__(self,game):
        self._game : Game = game
        self.gameName = "Empty Game"

        self._currentScene : ecs.Scene = None
        self.display : pygame.Surface = None
        self.running = False

        self._lastTickStart = 0
        self.deltaTime = 0
        self.frameStartTime = 0
        self.maxDeltaTime = 0.1 #Maximum delta time enforced to prevent unintended concequences of super high delta time.

        self._inputStates = {}
        self.scroll = 0
        Engine._instance = self

        self._queuedScene = None # LoadScene sets this, and the update loop will swap scenes if this isn't none.

        self.LoadGame() #Loads self._game into the engine
    def LoadGame(self):
        Log("Loading game into engine",LOG_INFO)
        self.gameName = self._game.name
        if(self._game.startingScene == None):
            Log("Game has no starting scene",LOG_ERRORS)
            exit(0)

        #Load splash screen if enabled otherwise load starting scene, if we load splash screen scene the splash screen scene swaps to the self._game.startingScene for us.
        if(self._game.startingSplashEnabled):
            self._currentScene = splashscene.engineSplashScreenScene
        else:
            self._currentScene = self._game.startingScene
        Log("Finished loading game into engine",LOG_INFO)

    async def Start(self):
        Log("Game Starting",LOG_INFO)
        self.Init()

        self.running = True
        self._lastTickStart = time.time()
        while self.running:
            self.frameStartTime = time.time()
            self.deltaTime = self.frameStartTime - self._lastTickStart
            if(self.deltaTime > self.maxDeltaTime): #Maximum delta time enforced to prevent unintended concequences of super high delta time.
                self.deltaTime = self.maxDeltaTime
            self._lastTickStart = self.frameStartTime

            #Check if there is a queued scene, if so swap to it.
            if(self._queuedScene != None):
                self._LoadQueuedScene()

            #Game Loop
            self.InputTick()
            self._currentScene.Update()

            await asyncio.sleep(0)
    def Init(self):
        Log("Game Initializing",LOG_INFO)
        pygame.init()
        pygame.mixer.init()
        self.display = pygame.display.set_mode((800,600))
        pygame.display.set_caption(self.gameName)
        if(self._game.icon != None):
            pygame.display.set_icon(self._game.icon)
        self.LoadScene(self._currentScene)

        Log("Game Initialized",LOG_INFO)

    def InputTick(self):

        #Go through and mark any KEYDOWN keys as KEYPRESSED and KEYUP keys as inactive.
        for key in self._inputStates.keys():
            if(self._inputStates[key] == KEYDOWN):
                self._inputStates[key] = KEYPRESSED
            elif(self._inputStates[key] == KEYUP):
                self._inputStates[key] = KEYINACTIVE

        #Check all the new pygame events for quitting and keys.
        for event in pygame.event.get():
            #Quit Button
            if(event.type == pygame.QUIT):
                self.Quit()
            #Keys
            elif(event.type == pygame.KEYDOWN):
                self._inputStates[event.key] = KEYDOWN
            elif(event.type == pygame.KEYUP):
                self._inputStates[event.key] = KEYUP
            #Scrolling
            elif(event.type == pygame.MOUSEWHEEL):
                self.scroll = event.y

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
    def LoadScene(self, scene : ecs.Scene):
        if(self._queuedScene != None):
            Log("Scene queuing on top of another scene. Before: "+self._queuedScene.name+", now: "+scene.name,LOG_WARNINGS)
        self._queuedScene = scene
        Log("Queued scene: "+scene.name,LOG_INFO)
    def _LoadQueuedScene(self):
        Log("Loading scene: "+self._queuedScene.name,LOG_INFO)
        self._currentScene = self._queuedScene
        self._queuedScene = None
        self._currentScene.game = self
        self._currentScene.Init()
    def GetCurrentScene(self):
        return self._currentScene
    def Quit(self):
        Log("Game Quitting",LOG_INFO)
        exit(0)

class Input:
    #Input class functions accessible via Input.KeyPressed, KeyDown, KeyUp
    def KeyPressed(key):
        return Engine._instance.KeyPressed(key)
    def KeyDown(key):
        return Engine._instance.KeyDown(key)
    def KeyUp(key):
        return Engine._instance.KeyUp(key)