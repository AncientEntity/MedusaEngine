import asyncio
import multiprocessing
import threading
from typing import Type

import pygame
import pygame._sdl2.controller
from _queue import Empty

import engine.ecs as ecs
from engine.constants import KEYDOWN, KEYUP, KEYPRESSED, KEYINACTIVE, SPLASH_BUILDONLY, SPLASH_ALWAYS, \
    NET_NONE, NET_HOST, NET_CLIENT, NET_EVENT_INIT, NET_EVENT_SNAPSHOT_PARTIAL, NET_EVENT_SNAPSHOT_FULL, \
    NET_LISTENSERVER, NET_PROCESS_OPEN_SERVER_TRANSPORT, NET_PROCESS_SHUTDOWN, NET_PROCESS_CONNECT_CLIENT_TRANSPORT, \
    NET_PROCESS_CLOSE_CLIENT_TRANSPORT, NET_PROCESS_CLOSE_SERVER_TRANSPORT, NET_PROCESS_CLIENT_SEND_MESSAGE, \
    NET_PROCESS_RECEIVE_MESSAGE, NET_PROCESS_SERVER_SEND_MESSAGE, NET_SUBPROCESS_NAME
from engine.datatypes.assetmanager import assets
from engine.game import Game
import time
from sys import exit
import sys
import platform

from engine.input import Input
from engine.logging import Log, LOG_ERRORS, LOG_INFO, LOG_WARNINGS, LOG_NETWORKING
from engine.networking.connectioninfo import ConnectionInfo
from engine.networking.connections.clientconnectionbase import ClientConnectionBase
from engine.networking.networkclientbase import NetworkClientBase
from engine.networking.networkevent import NetworkEvent, NetworkEventCreateEntity, NetworkEventToBytes, \
    NetworkEventFromBytes
from engine.networking.networkprocess import NetworkProcessMain, NetworkProcessMessage, NetworkUpdateTransport, \
    NetworkSendMessage
from engine.networking.networkserverbase import NetworkServerBase
from engine.networking.networksnapshot import NetworkSnapshot, NetworkEntitySnapshot
from engine.networking.networkstate import NetworkState
from engine.networking.transport.networktcptransport import NetworkTCPTransport
from engine.networking.transport.networkudptransport import NetworkUDPTransport
from engine.networking.variables.networkvarbase import NetworkVarBase
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
        self.deltaTime = 0 # Can be got anywhere via engine.time.Time.deltaTime
        self.frameStartTime = 0
        self.maxDeltaTime = 0.1 #Maximum delta time enforced to prevent unintended concequences of super high delta time.

        # Scene Loading
        self._lastLoadedScene = None # Last scene class to be loaded.
        self._queuedScene = None # LoadScene sets this, and the update loop will swap scenes if this isn't none.

        # Networking
        self.snapshotDelay = 10.0 / 60.0
        self.connections = []
        self.connectionsReference : dict[ClientConnectionBase, ConnectionInfo] = {} # key=ClientConnectionBase, value=ConnectionInfo

        self.clientInitialized = False
        self._queuedNetworkEvents = []
        self._networkSendQueue = []
        self._lastSnapshotTime = 0

        self._networkServer : NetworkServerBase = None
        self._networkClient : NetworkClientBase = None

        self._networkQueueIn : multiprocessing.Queue = None
        self._networkQueueOut : multiprocessing.Queue = None
        self._networkProcess : multiprocessing.Process = None


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
        if IsBuilt() and not IsPlatformWeb():
            multiprocessing.freeze_support() # Ensures freeze support with multiprocessing.

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

        if not IsPlatformWeb():
            self.NetworkCreateProcess()

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

        if NetworkState.identity & NET_CLIENT:
            self.NetworkClientDisconnect()
        if NetworkState.identity & NET_HOST:
            self.NetworkHostStop()

        if self._networkProcess:
            self.NetworkShutdownProcess()

        exit(0)

    def NetworkTick(self):
        # debug testing remove eventually
        if Input.KeyDown(pygame.K_LEFTBRACKET):
            self.NetworkHostStart('127.0.0.1', 25565)
        elif Input.KeyDown(pygame.K_RIGHTBRACKET):
            self.NetworkClientConnect('127.0.0.1', 25565)
        elif Input.KeyDown(pygame.K_n):
            for thread in threading.enumerate():
                print(thread.name)

        if NetworkState.identity == NET_NONE:
            return

        queueEmptyError = False
        while not queueEmptyError:
            try:
                nextMessage : NetworkProcessMessage = self._networkQueueOut.get(False)
            except Empty:
                queueEmptyError = True
                break
            if nextMessage.id == NET_PROCESS_RECEIVE_MESSAGE:
                self._queuedNetworkEvents.append(nextMessage.data)

        # Handle new queued network events
        for i in range(len(self._queuedNetworkEvents)):
            self.NetworkHandleEvent(self._queuedNetworkEvents.pop(0))

        # Snapshots
        curTime = time.time()
        if curTime - self._lastSnapshotTime >= self.snapshotDelay:
            self._lastSnapshotTime = curTime
            snapshot = NetworkSnapshot.GenerateSnapshotPartial(self._currentScene)
            bytesToSend = NetworkEventToBytes(NetworkEvent(NET_EVENT_SNAPSHOT_PARTIAL, snapshot.SnapshotToBytes()))

            if NetworkState.identity & NET_HOST:
                self.NetworkServerSend(bytesToSend, "tcp", None)
            elif NetworkState.identity & NET_CLIENT:
                self.NetworkClientSend(bytesToSend, "tcp")

    def NetworkCreateProcess(self):
        if not self._networkProcess:
            Log("Creating network process", LOG_NETWORKING)
            self._networkQueueIn = multiprocessing.Queue()
            self._networkQueueOut = multiprocessing.Queue()
            self._networkProcess = multiprocessing.Process(target=NetworkProcessMain, args=(self._networkQueueIn,
                                                                                            self._networkQueueOut))
            self._networkProcess.name = NET_SUBPROCESS_NAME
            self._networkProcess.daemon = True
            self._networkProcess.start()
    def NetworkShutdownProcess(self):
        Log("Shutting down network process", LOG_NETWORKING)
        self._networkQueueIn.put(NetworkProcessMessage(NET_PROCESS_SHUTDOWN, None))
        self._networkQueueIn.close()
        self._networkQueueOut.close()
        self._networkProcess = None

    def NetworkHostStart(self, ip, port):
        self._networkQueueIn.put(NetworkProcessMessage(NET_PROCESS_OPEN_SERVER_TRANSPORT,
                                                       NetworkUpdateTransport("tcp", NetworkTCPTransport, (ip, port))))
        #self._networkQueueIn.put(NetworkProcessMessage(NET_PROCESS_OPEN_SERVER_TRANSPORT,
        #                                               NetworkUpdateTransport("udp", NetworkUDPTransport, (ip, port + 1))))

        NetworkState.identity |= NET_HOST

        Log(f"Network Host Start, Identity: {NetworkState.identity}", LOG_NETWORKING)

    def NetworkHostStop(self):
        Log("Network Host Stop", LOG_NETWORKING)
        if not NetworkState.identity & NET_HOST:
            return

        self._networkQueueIn.put(NetworkProcessMessage(NET_PROCESS_CLOSE_SERVER_TRANSPORT,
                                                       NetworkUpdateTransport("tcp", None, None)))
        #self._networkQueueIn.put(NetworkProcessMessage(NET_PROCESS_CLOSE_SERVER_TRANSPORT,
        #                                               NetworkUpdateTransport("udp", None, None)))

        if NetworkState.identity | NET_HOST:
            NetworkState.identity -= NET_HOST

        Log(f"Network Host Stop, Identity: {NetworkState.identity}", LOG_NETWORKING)

    def NetworkClientConnect(self, ip : str, port : int):
        Log(f"Network Client Connect ({ip},{port})", LOG_NETWORKING)
        if self._networkClient:
            Log("Failed to NetworkClientConnect, network client already exists", LOG_ERRORS)

        self._networkQueueIn.put(NetworkProcessMessage(NET_PROCESS_CONNECT_CLIENT_TRANSPORT,
                                                       NetworkUpdateTransport("tcp", NetworkTCPTransport, (ip, port))))
        #self._networkQueueIn.put(NetworkProcessMessage(NET_PROCESS_CONNECT_CLIENT_TRANSPORT,
        #                                               NetworkUpdateTransport("udp", NetworkUDPTransport, (ip, port + 1))))

        NetworkState.identity |= NET_CLIENT

        networkEventBytes = NetworkEventToBytes(NetworkEvent(NET_EVENT_INIT, bytearray()))
        self.NetworkClientSend(networkEventBytes, "tcp")

        self.clientInitialized = False
        Log(f"Network Client Connect, Identity: {NetworkState.identity}", LOG_NETWORKING)

    def NetworkClientDisconnect(self):
        Log("Network Client Disconnect", LOG_NETWORKING)
        if not NetworkState.identity & NET_CLIENT:
            return


        self._networkQueueIn.put(NetworkProcessMessage(NET_PROCESS_CLOSE_CLIENT_TRANSPORT,
                                                       NetworkUpdateTransport("tcp", None, None)))
        #self._networkQueueIn.put(NetworkProcessMessage(NET_PROCESS_CLOSE_CLIENT_TRANSPORT,
        #                                               NetworkUpdateTransport("udp", None, None)))

        if NetworkState.identity | NET_CLIENT:
            NetworkState.identity -= NET_CLIENT

        Log(f"Network Client Disconnect, Identity: {NetworkState.identity}", LOG_NETWORKING)

    def NetworkHandleEvent(self, networkEvent : NetworkEvent):
        if networkEvent.eventId == NET_EVENT_INIT:
            if networkEvent.processAs & NET_CLIENT:
                NetworkState.clientId = int.from_bytes(networkEvent.data,"big")
                self.clientInitialized = True
                Log(f"Received Init Event, Client Id: {NetworkState.clientId}", LOG_NETWORKING)
                assets.NetInstantiate("player",self._currentScene, position=self._currentScene.GetRandomTiledObjectByName("SPAWN")["position"][:])
                # todo save client info to list somewhere and mark client as initialized and dont reply to NET_EVENT_INIT from the client anymore.
            elif networkEvent.processAs & NET_HOST:
                if networkEvent.sender in self.connectionsReference:
                    return # Already initialized the client.

                # send new connection it's client ID and such
                networkEventBytes = NetworkEventToBytes(NetworkEvent(NET_EVENT_INIT, networkEvent.sender.to_bytes(4,"big")))
                connectionInfo = ConnectionInfo(networkEvent.sender)
                self.connections.append(connectionInfo) # todo handle removing (disconnecting) from the list
                self.connectionsReference[networkEvent.sender] = connectionInfo
                self.NetworkServerSend(networkEventBytes, "tcp", networkEvent.sender)

                # send new connection full snapshot
                snapshot = NetworkSnapshot.GenerateSnapshotFull(self._currentScene) # todo sometimes just do partial snapshots
                bytesToSend = NetworkEventToBytes(NetworkEvent(NET_EVENT_SNAPSHOT_FULL, snapshot.SnapshotToBytes()))
                self.NetworkServerSend(bytesToSend, "tcp", networkEvent.sender)

                #self._networkServer.Send(networkEventBytes, networkEvent.sender, "tcp")
        if not self.clientInitialized and NetworkState.identity != NET_HOST:
            return

        if networkEvent.eventId == NET_EVENT_SNAPSHOT_PARTIAL or networkEvent.eventId == NET_EVENT_SNAPSHOT_FULL:
            snapshot = NetworkSnapshot.SnapshotFromBytes(networkEvent.data)
            #if networkEvent.sender:
            #    print(f"Handling snapshot from client={self.connectionsReference[networkEvent.sender].clientID}, entcount={len(snapshot.entities)}")
            self.NetworkHandleSnapshot(snapshot)
            # todo creating entities via snapshot
            # todo destroying entities via snapshot
            # todo updating variables over snapshot

    def NetworkHandleSnapshot(self, snapshot : NetworkSnapshot):
        netEntitySnapshot : NetworkEntitySnapshot
        for netEntitySnapshot in snapshot.entities:
            if netEntitySnapshot.prefabName == '' or netEntitySnapshot.ownerId == NetworkState.clientId:
                continue
            #todo check if entity marked for deletion

            # If entity doesnt exist create it
            if netEntitySnapshot.networkId not in self._currentScene.networkedEntities:
                ent = assets.NetInstantiate(netEntitySnapshot.prefabName, self._currentScene, netEntitySnapshot.networkId, netEntitySnapshot.ownerId, [0,0])
                #print(f"Replicating over network: {netEntitySnapshot.prefabName}, id: {netEntitySnapshot.networkId}, vars: {netEntitySnapshot.variables}")
            else:
                ent = self._currentScene.networkedEntities[netEntitySnapshot.networkId]

            entVars = ent.GetNetworkVariables()
            for variable in netEntitySnapshot.variables:
                for foundVar in entVars:
                    if foundVar[0] == variable[0]:
                        foundVar[1].SetFromBytes(variable[1], modified=False)
                        #print(f"Updated var entityId={netEntitySnapshot.networkId}, varname={variable[0]}, val={foundVar[1].Get()}")
                        break
    # If target is None, it will send all
    def NetworkServerSend(self, message, transport, target):
        self._networkQueueIn.put(NetworkProcessMessage(NET_PROCESS_SERVER_SEND_MESSAGE,
                                                       NetworkSendMessage(transport, target,
                                                                          message)))
    def NetworkClientSend(self, message, transport):
        self._networkQueueIn.put(NetworkProcessMessage(NET_PROCESS_CLIENT_SEND_MESSAGE, NetworkSendMessage(transport, None, message)))