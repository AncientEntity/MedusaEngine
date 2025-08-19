import asyncio
import multiprocessing
import threading
from typing import Type

import pygame
import pygame._sdl2.controller

from engine import ecs
from engine.constants import *
from engine.datatypes.assetmanager import assets
from engine.game import Game
import time
from sys import exit
import sys
import os
import platform
import engine.tools.platform

from engine.input import Input
from engine.logging import Log, LOG_ERRORS, LOG_INFO, LOG_WARNINGS, LOG_NETWORKING
from engine.networking.connectioninfo import ConnectionInfo
from engine.networking.connections.clientconnectionbase import ClientConnectionBase
from engine.networking.networkclientbase import NetworkClientBase
from engine.networking.networkevent import NetworkEvent, NetworkEventToBytes
from engine.networking.networkserverbase import NetworkServerBase
from engine.networking.networksnapshot import NetworkSnapshot, NetworkEntitySnapshot
from engine.networking.networkstate import NetworkState
from engine.networking.rpc import RPCAction
from engine.networking.transport.networktcptransport import NetworkTCPTransport
from engine.networking.transport.networkudptransport import NetworkUDPTransport
from engine.scenes import splashscene
from engine.tools.platform import IsBuilt, IsDebug, currentPlatform, IsPlatformWeb
if not IsPlatformWeb():
    import zmq
    from engine.networking.networkprocess import NetworkProcessMain, NetworkProcessMessage, NetworkUpdateTransport, \
    NetworkSendMessage, NetworkDisconnect


class Engine:
    _instance = None
    def __init__(self,game):
        Engine._instance = self

        self._game : Game = game
        self.gameName = "Empty Game"

        self._currentScene : ecs.Scene = None
        self.running = False

        self.headless = "headless" in sys.argv
        engine.tools.platform.headless = self.headless

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
        if not IsPlatformWeb():
            self.snapshotDelay = 1.0 / 25.0
            self.connections = []
            self.connectionsReference : dict[int, ConnectionInfo] = {} # key=ClientConnectionBase, value=ConnectionInfo

            self.clientInitialized = False
            self._queuedNetworkEvents = []
            self._networkSendQueue = []
            self._lastSnapshotTime = 0

            self._networkServer : NetworkServerBase = None
            self._networkClient : NetworkClientBase = None

            self._netContext : zmq.Context = zmq.Context()
            self._networkProcessSocket : zmq.Socket = None
            self._networkProcess : multiprocessing.Process = None


        self.LoadGame() #Loads self._game into the engine
    def LoadGame(self):
        Log(f"Loading game into engine (headless={self.headless})",LOG_INFO)
        self.gameName = self._game.name
        if(self._game.startingScene == None):
            Log("Game has no starting scene",LOG_ERRORS)
            exit(0)

        if(self._game.webCanvasPixelated):
            if sys.platform == 'emscripten':
                platform.window.canvas.style.imageRendering = "pixelated"

        #Load splash screen if enabled otherwise load starting scene, if we load splash screen scene the splash screen scene swaps to the self._game.startingScene for us.
        if(not engine.tools.platform.headless and (self._game.startingSplashMode == SPLASH_ALWAYS or (IsBuilt() and
                                                              self._game.startingSplashMode == SPLASH_BUILDONLY))):
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

            # Input Tick
            Input.InputTick()

            # Network Tick
            self.NetworkTick()

            #Game Loop
            if Input.quitPressed:
                self.Quit()
            self._currentScene.Update()

            await asyncio.sleep(0)
    def Init(self):
        Log(f"Game Initializing (IsBuilt:{IsBuilt()}, IsDebug:{IsDebug()}, Platform:{currentPlatform})",LOG_INFO)

        if not IsPlatformWeb():
            self.NetworkCreateProcess()

        if engine.tools.platform.headless:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            os.environ["SDL_AUDIODRIVER"] = "dummy"

        pygame.init()
        if not engine.tools.platform.headless:
            pygame.mixer.init()
            pygame.joystick.init()
            pygame._sdl2.controller.init()

        Input.Init(self._game.inputActions)

        if not self.headless:
            self.CreateDisplay()

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

    def CreateDisplay(self):
        self.displayFlags = pygame.FULLSCREEN if self._game.startFullScreen else 0
        self.displayFlags |= pygame.RESIZABLE if self._game.resizableWindow and not IsPlatformWeb() else 0
        self.display = pygame.display.set_mode(self._game.windowSize, self.displayFlags)
        pygame.display.set_caption(
            f"{self.gameName}{'' if not IsDebug() else f' (Debug Environment, Platform: {currentPlatform})'}")
        if (self._game.icon == None):
            self._game.icon = pygame.image.load("engine/art/logo-dark.png")
        pygame.display.set_icon(self._game.icon)
        Log(f"Display Created: {pygame.display.Info()}", LOG_INFO)

    def NetworkTick(self):
        if NetworkState.identity == NET_NONE:
            return

        messageWaiting = True
        while messageWaiting:
            try:
                nextMessage = self._networkProcessSocket.recv_pyobj(zmq.NOBLOCK)
            except zmq.error.ZMQError:
                messageWaiting = False
                break

            processDelay = time.time() - nextMessage.requestMade
            if processDelay > NET_SAFE_PROCESS_DELAY:
                Log(f"Warning engine process delay above safe constant. Process Delay: {processDelay}", LOG_NETWORKING)

            if nextMessage.id == NET_PROCESS_RECEIVE_MESSAGE:
                self._queuedNetworkEvents.append(nextMessage.data)
            elif nextMessage.id == NET_PROCESS_CLIENT_CONNECT:
                NetworkState.TriggerHook(NetworkState.onClientConnect, (nextMessage.data.referenceId,))
                Log(f"New Client Connected: {nextMessage.data.referenceId}, {nextMessage.data.nickname}", LOG_NETWORKING)
            elif nextMessage.id == NET_PROCESS_CLIENT_DISCONNECT:
                self.RemoveConnection(nextMessage.data.referenceId)
                NetworkState.TriggerHook(NetworkState.onClientDisconnect, (nextMessage.data.referenceId,))
                Log(f"Client Disconnected: {nextMessage.data.referenceId}, {nextMessage.data.nickname}", LOG_NETWORKING)
            elif nextMessage.id == NET_PROCESS_CONNECT_SUCCESS:
                Log(f"Connected to {nextMessage.data.ipandport}", LOG_NETWORKING)
            elif nextMessage.id == NET_PROCESS_CONNECT_FAIL:
                NetworkState.TriggerHook(NetworkState.onConnectFail, (nextMessage.data,))
                Log(f"Failed to connect to {nextMessage.data.ipandport}", LOG_NETWORKING)
            elif nextMessage.id == NET_PROCESS_DISCONNECT:
                networkDisconnect : NetworkDisconnect = nextMessage.data
                NetworkState.TriggerHook(NetworkState.onDisconnect, (networkDisconnect.reason,networkDisconnect.transportName))
                Log(f"Client Disconnected from server {networkDisconnect.transportName}")
            else:
                Log(f"Engine Unknown message type received: {nextMessage}", LOG_NETWORKING)

        # Handle new queued network events
        while len(self._queuedNetworkEvents) > 0:
            self.NetworkHandleEvent(self._queuedNetworkEvents.pop(0))

        if not self.clientInitialized and not NetworkState.identity & NET_HOST:
            return

        # Snapshots
        curTime = time.time()
        if curTime - self._lastSnapshotTime >= self.snapshotDelay:
            self._lastSnapshotTime = curTime
            if NetworkState.identity & NET_HOST:
                snapshot = NetworkSnapshot.GenerateSnapshotFull(self._currentScene)
                bytesToSend = NetworkEventToBytes(NetworkEvent(NET_EVENT_SNAPSHOT_PARTIAL, snapshot.SnapshotToBytes()))
            elif NetworkState.identity & NET_CLIENT:
                snapshot = NetworkSnapshot.GenerateSnapshotPartial(self._currentScene)
                bytesToSend = NetworkEventToBytes(NetworkEvent(NET_EVENT_SNAPSHOT_PARTIAL, snapshot.SnapshotToBytes()))
            NetworkState.rpcQueue.clear()
            self._currentScene.networkDeletedQueue.clear()

            if NetworkState.identity & NET_HOST:
                self.NetworkServerSend(bytesToSend, "udp", None)
            elif NetworkState.identity & NET_CLIENT:
                self.NetworkClientSend(bytesToSend, "udp")

    def NetworkCreateProcess(self):
        if not self._networkProcess:
            Log("Creating network process", LOG_NETWORKING)

            self._networkProcessSocket = self._netContext.socket(zmq.PAIR)
            portUsed = self._networkProcessSocket.bind_to_random_port('tcp://localhost', min_port=30000)

            self._networkProcess = multiprocessing.Process(target=NetworkProcessMain, args=(portUsed,))
            self._networkProcess.name = NET_SUBPROCESS_NAME
            self._networkProcess.daemon = True
            self._networkProcess.start()
            subprocessAck = self._networkProcessSocket.recv(4)
            if subprocessAck != b"ack":
                Log(f"Incorrect acknowledgement from network subprocess. Port: {portUsed}", LOG_NETWORKING)
            else:
                Log(f"Acknowledgement receieved from network subprocess Port: {portUsed}", LOG_NETWORKING)

    def NetworkShutdownProcess(self):
        Log("Shutting down network process", LOG_NETWORKING)
        self._networkProcessSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_SHUTDOWN, None))
        self._networkProcessSocket.close()
        self._networkProcess = None

    def NetworkHostStart(self, ip, port):
        self._networkProcessSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_OPEN_SERVER_TRANSPORT,
                                                                    NetworkUpdateTransport("udp", NetworkUDPTransport, (ip, port))))

        NetworkState.identity |= NET_HOST

        Log(f"Network Host Start, Identity: {NetworkState.identity}", LOG_NETWORKING)

    def NetworkHostStop(self):
        Log("Network Host Stop", LOG_NETWORKING)
        if not NetworkState.identity & NET_HOST:
            return
        self._networkProcessSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_CLOSE_SERVER_TRANSPORT,
                                                                    NetworkUpdateTransport("udp", None, None)))

        if NetworkState.identity & NET_HOST:
            NetworkState.identity -= NET_HOST

        Log(f"Network Host Stop, Identity: {NetworkState.identity}", LOG_NETWORKING)

    def NetworkServerKick(self, clientId : int):
        self._networkProcessSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_KICK_CLIENT,
                                                                    clientId))

    def NetworkClientConnect(self, ip : str, port : int):
        Log(f"Network Client Connect ({ip},{port})", LOG_NETWORKING)
        if self._networkClient:
            Log("Failed to NetworkClientConnect, network client already exists", LOG_ERRORS)

        self._networkProcessSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_CONNECT_CLIENT_TRANSPORT,
                                                                    NetworkUpdateTransport("udp", NetworkUDPTransport, (ip, port))))

        NetworkState.identity |= NET_CLIENT

        networkEventBytes = NetworkEventToBytes(NetworkEvent(NET_EVENT_INIT, bytearray()))
        self.NetworkClientSend(networkEventBytes, "udp")

        self.clientInitialized = False
        Log(f"Network Client Connect, Identity: {NetworkState.identity}", LOG_NETWORKING)

    def NetworkClientDisconnect(self):
        Log("Network Client Disconnect", LOG_NETWORKING)
        if not NetworkState.identity & NET_CLIENT:
            return

        self._networkProcessSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_CLOSE_CLIENT_TRANSPORT,
                                                                    NetworkUpdateTransport("udp", None, None)))

        if NetworkState.identity & NET_CLIENT:
            NetworkState.identity -= NET_CLIENT

        Log(f"Network Client Disconnect, Identity: {NetworkState.identity}", LOG_NETWORKING)

    def NetworkHandleEvent(self, networkEvent : NetworkEvent):
        if networkEvent.eventId == NET_EVENT_INIT:
            if networkEvent.processAs & NET_CLIENT:
                NetworkState.clientId = int.from_bytes(networkEvent.data,"big")
                self.clientInitialized = True
                NetworkState.TriggerHook(NetworkState.onConnectSuccess, ())
                Log(f"Received Init Event, Client Id: {NetworkState.clientId}", LOG_NETWORKING)
            elif networkEvent.processAs & NET_HOST:
                if networkEvent.sender in self.connectionsReference:
                    return # Already initialized the client.

                # send new connection it's client ID and such
                networkEventBytes = NetworkEventToBytes(NetworkEvent(NET_EVENT_INIT, networkEvent.sender.to_bytes(4,"big")))
                self.AddConnection(networkEvent.sender)
                self.NetworkServerSend(networkEventBytes, "udp", networkEvent.sender)

                # send new connection full snapshot
                snapshot = NetworkSnapshot.GenerateSnapshotFull(self._currentScene) # todo net sometimes just do partial snapshots
                bytesToSend = NetworkEventToBytes(NetworkEvent(NET_EVENT_SNAPSHOT_FULL, snapshot.SnapshotToBytes()))
                self.NetworkServerSend(bytesToSend, "udp", networkEvent.sender)

        if not self.clientInitialized and NetworkState.identity != NET_HOST:
            return
        if NetworkState.identity & NET_HOST and networkEvent.sender not in self.connectionsReference:
            return

        if networkEvent.eventId == NET_EVENT_SNAPSHOT_PARTIAL or networkEvent.eventId == NET_EVENT_SNAPSHOT_FULL:
            self.NetworkHandleSnapshot(networkEvent)

    def NetworkHandleSnapshot(self, networkEvent : NetworkEvent):
        snapshot : NetworkSnapshot = NetworkSnapshot.SnapshotFromBytes(networkEvent.data)

        # Prevent input tampering of other clients
        if NetworkState.identity & NET_HOST:
            if networkEvent.sender in snapshot.actionStates:
                snapshot.actionStates = {networkEvent.sender : snapshot.actionStates[networkEvent.sender]}
            else:
                snapshot.actionStates = {}
        if NetworkState.identity & NET_CLIENT:
            if NetworkState.clientId in snapshot.actionStates:
                snapshot.actionStates.pop(NetworkState.clientId) # Prevents server from modifying local inputs

        Input.UpdateNetworkActionState(snapshot.actionStates)

        netEntitySnapshot : NetworkEntitySnapshot
        for netEntitySnapshot in snapshot.entities:
            # Can only replicate prefabs at the moment
            if netEntitySnapshot.prefabName == '':
                continue
            entityFound = netEntitySnapshot.networkId in self._currentScene.networkedEntities

            # If entity doesnt exist create it
            ent = None
            if not entityFound:
                if not netEntitySnapshot.markDeletion:
                    ent = assets.NetInstantiate(netEntitySnapshot.prefabName, self._currentScene, netEntitySnapshot.networkId, netEntitySnapshot.ownerId, [0,0])
            else:
                ent = self._currentScene.networkedEntities[netEntitySnapshot.networkId]
            if netEntitySnapshot.markDeletion:
                if ent:
                    self._currentScene.DeleteEntity(ent, False if not NetworkState.identity & NET_HOST else True)
                continue


            entVars = ent.GetNetworkVariables()
            for variable in netEntitySnapshot.variables:
                for foundVar in entVars:
                    if foundVar[1].prioritizeOwner and netEntitySnapshot.ownerId == NetworkState.clientId:
                        continue

                    if foundVar[0] == variable[0] and not foundVar[1].AreBytesEqual(variable[1]):
                        foundVar[1].SetFromBytes(variable[1], modified=False)
                        break


        if networkEvent.sender == NetworkState.clientId:
            return

        rpc : RPCAction
        for rpc in snapshot.rpcCalls:

            system = self._currentScene.GetSystemByName(rpc.systemType) #todo net GetSystemByName is slow. Use dict instead.
            funcToCall = getattr(system, rpc.funcName)
            if not hasattr(funcToCall, "__rpc__"):
                Log(f"ClientId: {networkEvent.sender} has tried to run non RPC function: {rpc.systemType}.{rpc.funcName}", LOG_WARNINGS)
                continue
            if NetworkState.identity & NET_HOST:
                if funcToCall.__rpc__['serverAuthorityRequired'] and NetworkState.clientId != networkEvent.sender:
                    Log(f"ClientId: {networkEvent.sender} tried to run a RPC function that is serverOnly: {rpc.systemType}.{rpc.funcName}", LOG_WARNINGS)
                    continue
                NetworkState.rpcQueue.append(rpc)

            funcToCall(self=system, argBytes=rpc.args, isCaller=False)



    def AddConnection(self, sender):
        connectionInfo = ConnectionInfo(sender)
        self.connections.append(connectionInfo)
        self.connectionsReference[sender] = connectionInfo
    def RemoveConnection(self, sender):
        conn : ConnectionInfo = None
        for conn in self.connections:
            if conn.connectionReferenceId == sender:
                break
        if conn:
            self.connections.remove(conn)
            self.connectionsReference.pop(sender)

            #Remove sender from input network state
            currentNetworkState = Input.GetNetworkActionState()
            if sender in currentNetworkState:
                currentNetworkState.pop(sender)

    # If target is None, it will send all
    def NetworkServerSend(self, message, transport, target):
        self._networkProcessSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_SERVER_SEND_MESSAGE,
                                                                    NetworkSendMessage(transport, target,
                                                                          message, NetworkState.clientId if NetworkState.clientId != -1 else None)))

    def NetworkClientSend(self, message, transport):
        self._networkProcessSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_CLIENT_SEND_MESSAGE, NetworkSendMessage(transport, None, message, None)))
