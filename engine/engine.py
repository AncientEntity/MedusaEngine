import asyncio
from typing import Type

import pygame
import pygame._sdl2.controller
import engine.ecs as ecs
from engine.constants import KEYDOWN, KEYUP, KEYPRESSED, KEYINACTIVE, SPLASH_BUILDONLY, SPLASH_ALWAYS, \
    NET_EVENT_ENTITY_CREATE, NET_EVENT_ENTITY_DELETE
from engine.datatypes.assetmanager import assets
from engine.game import Game
import time
from sys import exit
import sys
import platform

from engine.input import Input
from engine.logging import Log, LOG_ERRORS, LOG_INFO, LOG_WARNINGS
from engine.networking.networkevent import NetworkEvent, NetworkEventCreateEntity
from engine.scenes import splashscene
from engine.tools.platform import IsBuilt, IsDebug, currentPlatform, IsPlatformWeb


class Engine:
    _instance = None
    def __init__(self,game):
        Engine._instance = self

        self._game : Game = game
        self.gameName = "Empty Game"

        self._currentScene : ecs.Scene = None
        self.running = False

        # Display
        self.display : pygame.Surface = None
        self.displayFlags = 0

        # Delta Time
        self._lastTickStart = 0
        self.deltaTime = 0
        self.frameStartTime = 0
        self.maxDeltaTime = 0.1 #Maximum delta time enforced to prevent unintended concequences of super high delta time.

        # Scene Loading
        self._lastLoadedScene = None # Last scene class to be loaded.
        self._queuedScene = None # LoadScene sets this, and the update loop will swap scenes if this isn't none.

        # Networking
        self._queuedNetworkEvents = []


        self.LoadGame() #Loads self._game into the engine
    def LoadGame(self):
        Log("Loading game into engine",LOG_INFO)
        self.gameName = self._game.name
        if(self._game.startingScene == None):
            Log("Game has no starting scene",LOG_ERRORS)
            exit(0)

        if(self._game.webCanvasPixelated):
            if sys.platform == 'emscripten':
                platform.window.canvas.style.imageRendering = "pixelated"

        #Load splash screen if enabled otherwise load starting scene, if we load splash screen scene the splash screen scene swaps to the self._game.startingScene for us.
        if(self._game.startingSplashMode == SPLASH_ALWAYS or (IsBuilt() and
                                                              self._game.startingSplashMode == SPLASH_BUILDONLY)):
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

            # Network Tick
            self.NetworkTick()

            #Game Loop
            Input.InputTick()
            if Input.quitPressed:
                self.Quit()
            self._currentScene.Update()

            if Input.KeyDown(pygame.K_UP):
                self._queuedNetworkEvents.append(NetworkEvent(NET_EVENT_ENTITY_CREATE, NetworkEventCreateEntity("particletest", (0,0)).ToBytes()))

            await asyncio.sleep(0)
    def Init(self):
        Log(f"Game Initializing (IsBuilt:{IsBuilt()}, IsDebug:{IsDebug()}, Platform:{currentPlatform})",LOG_INFO)
        pygame.init()
        pygame.mixer.init()
        pygame.joystick.init()
        pygame._sdl2.controller.init()

        Input.Init()

        self.displayFlags = pygame.FULLSCREEN if self._game.startFullScreen else 0
        self.displayFlags |= pygame.RESIZABLE if self._game.resizableWindow and not IsPlatformWeb() else 0
        self.display = pygame.display.set_mode(self._game.windowSize, self.displayFlags)
        pygame.display.set_caption(f"{self.gameName}{'' if not IsDebug() else f' (Debug Environment, Platform: {currentPlatform})'}")
        if(self._game.icon == None):
            self._game.icon = pygame.image.load("engine/art/logo-dark.png")
        pygame.display.set_icon(self._game.icon)
        Log(f"Display Created: {pygame.display.Info()}", LOG_INFO)

        self.LoadScene(self._currentScene)

        Log("Game Initialized",LOG_INFO)

    def LoadScene(self, scene : Type[ecs.Scene]):
        self._lastLoadedScene = scene
        sceneInstance = scene()
        if(self._queuedScene != None):
            Log("Scene queuing on top of another scene. Before: "+self._queuedScene.name+", now: "+sceneInstance.name,LOG_WARNINGS)
        self._queuedScene = sceneInstance
        Log("Queued scene: "+self._queuedScene.name,LOG_INFO)
    def ReloadScene(self):
        self.LoadScene(self._lastLoadedScene)
    def _LoadQueuedScene(self):
        Log("Loading scene: "+self._queuedScene.name,LOG_INFO)

        if isinstance(self._currentScene, ecs.Scene):
            self._currentScene.Disable()

        self._currentScene = self._queuedScene
        self._queuedScene = None
        self._currentScene.game = self
        self._currentScene.Init()
    def GetCurrentScene(self):
        return self._currentScene
    def Quit(self):
        Log("Game Quitting",LOG_INFO)
        exit(0)

    def NetworkTick(self):
        for i in range(len(self._queuedNetworkEvents)):
            self.NetworkHandleEvent(self._queuedNetworkEvents.pop(0))

    def NetworkHandleEvent(self, networkEvent : NetworkEvent):
        if networkEvent.eventId == NET_EVENT_ENTITY_CREATE:
            createEvent = NetworkEventCreateEntity.FromBytes(networkEvent.data)
            newEntity = assets.Instantiate(createEvent.prefab_name, self._currentScene)
            newEntity.position = createEvent.position
            # todo figure out id syncing, might need to just have an OverrideId method
            Log(f"Created {createEvent.prefab_name} at position {createEvent.position}")
        elif networkEvent.eventId == NET_EVENT_ENTITY_DELETE:
            pass