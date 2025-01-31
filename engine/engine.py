import asyncio
from typing import Type

import pygame
import pygame._sdl2.controller
import engine.ecs as ecs
from engine.constants import KEYDOWN, KEYUP, KEYPRESSED, KEYINACTIVE, SPLASH_BUILDONLY, SPLASH_ALWAYS, \
    NET_EVENT_ENTITY_CREATE, NET_EVENT_ENTITY_DELETE, NET_NONE, NET_HOST, NET_CLIENT, NET_EVENT_INIT
from engine.datatypes.assetmanager import assets
from engine.game import Game
import time
from sys import exit
import sys
import platform

from engine.input import Input
from engine.logging import Log, LOG_ERRORS, LOG_INFO, LOG_WARNINGS, LOG_NETWORKING
from engine.networking.networkclientbase import NetworkClientBase
from engine.networking.networkevent import NetworkEvent, NetworkEventCreateEntity, NetworkEventToBytes, \
    NetworkEventFromBytes
from engine.networking.networkserverbase import NetworkServerBase
from engine.networking.transport.networktcptransport import NetworkTCPTransport
from engine.networking.transport.networkudptransport import NetworkUDPTransport
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
        self.identity = NET_HOST
        self.clientId = -1
        self._lastClientId = -1
        self._queuedNetworkEvents = []
        self._networkSendQueue = []

        self._networkServer : NetworkServerBase = None
        self._networkClient : NetworkClientBase = None


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
        if self._networkClient:
            nextMessageBytes = self._networkClient.GetNextMessage()
            if nextMessageBytes:
                nextMessage = NetworkEventFromBytes(nextMessageBytes[0])
                nextMessage.processAs = NET_CLIENT
                self._queuedNetworkEvents.append(nextMessage)
                print(nextMessage)

        if self._networkServer:
            nextMessageBytes = self._networkServer.GetNextMessage()
            if nextMessageBytes:
                nextMessage = NetworkEventFromBytes(nextMessageBytes[0])
                nextMessage.processAs = NET_HOST
                nextMessage.sender = nextMessageBytes[1]
                self._queuedNetworkEvents.append(nextMessage)

        for i in range(len(self._queuedNetworkEvents)):
            self.NetworkHandleEvent(self._queuedNetworkEvents.pop(0))

        if Input.KeyDown(pygame.K_LEFTBRACKET):
            self.NetworkHostStart('127.0.0.1', 25565)
        elif Input.KeyDown(pygame.K_RIGHTBRACKET):
            self.NetworkClientConnect('127.0.0.1', 25565)

    def NetworkHostStart(self, ip, port):
        if self._networkServer:
            Log("Failed to NetworkHostStart, network server already exists", LOG_ERRORS)

        self._networkServer = NetworkServerBase()
        self._networkServer.Open("tcp", NetworkTCPTransport(), (ip, port))
        self._networkServer.Open("udp", NetworkUDPTransport(), (ip, port+1))
        self.identity |= NET_HOST

        Log(f"Network Host Start, Identity: {self.identity}", LOG_NETWORKING)

    def NetworkHostStop(self):
        Log("Network Host Stop", LOG_NETWORKING)
        self._networkServer.Close("tcp")
        self._networkServer.Close("udp")

        if self.identity | NET_HOST:
            self.identity -= NET_HOST

        Log(f"Network Host Stop, Identity: {self.identity}", LOG_NETWORKING)

    def NetworkClientConnect(self, ip : str, port : int):
        Log(f"Network Client Connect ({ip},{port})", LOG_NETWORKING)
        if self._networkClient:
            Log("Failed to NetworkClientConnect, network client already exists", LOG_ERRORS)

        self._networkClient = NetworkClientBase()
        self._networkClient.Connect("tcp", NetworkTCPTransport(), (ip, port))
        self._networkClient.Connect("udp", NetworkUDPTransport(), (ip, port+1))
        self.identity |= NET_CLIENT

        networkEventBytes = NetworkEventToBytes(NetworkEvent(NET_EVENT_INIT, bytearray()))
        self._networkClient.Send(networkEventBytes, "tcp")

        Log(f"Network Client Connect, Identity: {self.identity}", LOG_NETWORKING)

    def NetworkClientDisconnect(self):
        Log("Network Client Disconnect", LOG_NETWORKING)
        self._networkClient.Close("tcp")
        self._networkClient.Close("udp")

        if self.identity | NET_CLIENT:
            self.identity -= NET_CLIENT

        Log(f"Network Client Disconnect, Identity: {self.identity}", LOG_NETWORKING)

    def NetworkHandleEvent(self, networkEvent : NetworkEvent):
        if networkEvent.eventId == NET_EVENT_INIT:
            if networkEvent.processAs & NET_CLIENT:
                self.clientId = int.from_bytes(networkEvent.data,"big")
                Log(f"Received Init Event, Client Id: {self.clientId}", LOG_NETWORKING)
                # todo save client info to list somewhere and mark client as initialized and dont reply to NET_EVENT_INIT from the client anymore.
            elif networkEvent.processAs & NET_HOST:
                self._lastClientId += 1
                networkEventBytes = NetworkEventToBytes(NetworkEvent(NET_EVENT_INIT, self._lastClientId.to_bytes(4,"big")))
                self._networkServer.Send(networkEventBytes, networkEvent.sender, "tcp")
                print('got and returning')

        elif networkEvent.eventId == NET_EVENT_ENTITY_CREATE:
            createEvent = NetworkEventCreateEntity.FromBytes(networkEvent.data)
            newEntity = assets.Instantiate(createEvent.prefab_name, self._currentScene)
            newEntity.position = createEvent.position
            # todo figure out id syncing, might need to just have an OverrideId method
            Log(f"Created {createEvent.prefab_name} at position {createEvent.position}")
        elif networkEvent.eventId == NET_EVENT_ENTITY_DELETE:
            pass