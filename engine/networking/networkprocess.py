import threading, time
from collections import namedtuple

import zmq

from engine.constants import NET_PROCESS_SHUTDOWN, NET_PROCESS_OPEN_SERVER_TRANSPORT, \
    NET_PROCESS_CLOSE_SERVER_TRANSPORT, NET_PROCESS_CONNECT_CLIENT_TRANSPORT, NET_PROCESS_CLOSE_CLIENT_TRANSPORT, \
    NET_PROCESS_CLIENT_SEND_MESSAGE, NET_PROCESS_SERVER_SEND_MESSAGE, NET_CLIENT, NET_PROCESS_RECEIVE_MESSAGE, NET_HOST, \
    NET_SAFE_PROCESS_DELAY, NET_PROCESS_CLIENT_CONNECT, NET_PROCESS_CONNECT_SUCCESS, NET_PROCESS_CONNECT_FAIL, \
    NET_PROCESS_CLIENT_DISCONNECT, NET_USER_DISCONNECTED, NET_PROCESS_DISCONNECT, NET_CONNECTION_LOST, \
    NET_PROCESS_KICK_CLIENT, NET_PROCESS_EVENT_ON_TRANSPORT_OPEN
from engine.logging import Log, LOG_NETWORKING, LOG_NETWORKPROCESS
from engine.networking.connections.clientconnectionbase import ClientConnectionBase
from engine.networking.networkclientbase import NetworkClientBase
from engine.networking.networkevent import NetworkEventFromBytes
from engine.networking.networkserverbase import NetworkServerBase
from engine.tools.platform import IsBuilt


class NetworkProcessMessage:
    def __init__(self, id, data):
        self.id : int = id
        self.data = data
        self.requestMade : float = time.time()

NetworkUpdateTransport = namedtuple('NetworkUpdateTransport', ['name', 'transport', 'ipandport'])

NetworkSendMessage = namedtuple('NetworkSendMessage', ['transportName', 'target', 'msgBytes', 'ignoreTarget'])

NetworkConnectionStatus = namedtuple('NetworkConnectionStatus', ['referenceId', 'isConnected', 'nickname'])

NetworkDisconnect = namedtuple('NetworkDisconnect', ['reason', 'transportName'])

active = True
networkServer: NetworkServerBase = None
networkClient: NetworkClientBase = None
processSocket = []
connections = {}
context: zmq.Context = zmq.Context()

def NetworkProcessMain(portUsed : int):
    global networkServer, networkClient, active, connections, processSocket
    #todo log files should have a different prefix set like log-net-* right now 2 files are generated.
    Log("Network Process Main Started", LOG_NETWORKPROCESS)

    processSocket = context.socket(zmq.PAIR)
    processSocket.connect(f"tcp://localhost:{portUsed}")
    processSocket.send(b"ack")

    receiveThread = threading.Thread(target=NetworkProcessReceiveThread, args=())
    receiveThread.start()

    active = True
    while active:
        nextMessage : NetworkProcessMessage = processSocket.recv_pyobj()

        processDelay = time.time() - nextMessage.requestMade
        if processDelay > NET_SAFE_PROCESS_DELAY:
            Log(f"Warning process delay above safe constant. Process Delay: {processDelay}", LOG_NETWORKPROCESS)

        if nextMessage.id == NET_PROCESS_SHUTDOWN:
            active = False

            if networkServer:
                for layer in list(networkServer.transportHandlers.keys()):
                    networkServer.Close(layer)
            if networkClient:
                for layer in list(networkClient.transportHandlers.keys()):
                    networkClient.Close(layer)

            processSocket.close()
            Log("Network Process Main Shutdown", LOG_NETWORKPROCESS)
            exit(0)

        # open close server transport
        elif nextMessage.id == NET_PROCESS_OPEN_SERVER_TRANSPORT:
            OpenServerTransport(nextMessage)
            continue
        elif nextMessage.id == NET_PROCESS_CLOSE_SERVER_TRANSPORT:
            CloseServerTransport(nextMessage)
            continue

        # connect / close client transport
        elif nextMessage.id == NET_PROCESS_CONNECT_CLIENT_TRANSPORT:
            ConnectClientTransport(nextMessage)
            continue
        elif nextMessage.id == NET_PROCESS_CLOSE_CLIENT_TRANSPORT:
            CloseClientTransport(nextMessage)
            continue

        # server kick user
        elif nextMessage.id == NET_PROCESS_KICK_CLIENT:
            if nextMessage.data not in connections:
                continue

            for layer in list(networkServer.transportHandlers.values()):
                layer.Kick(connections[nextMessage.data])
                NetworkClientDisconnect(connections[nextMessage.data])
                Log(f"Client {nextMessage.data} kicked on layer {type(layer)}")


        # send messages
        elif nextMessage.id == NET_PROCESS_CLIENT_SEND_MESSAGE:
            sendMessageInfo : NetworkSendMessage = nextMessage.data
            if sendMessageInfo.transportName not in networkClient.transportHandlers:
                Log(f"No transport handler called {sendMessageInfo.transportName} for client", LOG_NETWORKPROCESS)
                continue

            try:
                networkClient.Send(sendMessageInfo.msgBytes, sendMessageInfo.transportName)
            except Exception as e:
                Log(f"Networking connection lost: {e}", LOG_NETWORKPROCESS)
                CloseClientTransport(NetworkProcessMessage(NET_PROCESS_CLOSE_CLIENT_TRANSPORT,
                                                           NetworkUpdateTransport(sendMessageInfo.transportName, None, None)), e)
                #CloseClientTransport(sendMessageInfo.transportName, e)
            continue

        elif nextMessage.id == NET_PROCESS_SERVER_SEND_MESSAGE:
            sendMessageInfo : NetworkSendMessage = nextMessage.data
            if sendMessageInfo.target is None:
                networkServer.SendAll(sendMessageInfo.msgBytes, sendMessageInfo.transportName, [sendMessageInfo.ignoreTarget])
            else:
                networkServer.Send(sendMessageInfo.msgBytes, connections[sendMessageInfo.target], sendMessageInfo.transportName)
            continue
        else:
            Log(f"Networking Unknown message type received: {nextMessage}", LOG_NETWORKPROCESS)

    processSocket.close()

def OpenServerTransport(nextMessage : NetworkProcessMessage):
    global networkServer
    openTransportInfo: NetworkUpdateTransport = nextMessage.data
    if not networkServer:
        networkServer = NetworkServerBase()
    networkServer.Open(openTransportInfo.name, openTransportInfo.transport(), openTransportInfo.ipandport)
    networkServer.transportHandlers[openTransportInfo.name].onClientConnect.append(NetworkClientConnect)
    networkServer.transportHandlers[openTransportInfo.name].onClientDisconnect.append(NetworkClientDisconnect)
    Log(f"STransport Opened {openTransportInfo.name} on ipandport={openTransportInfo.ipandport}", LOG_NETWORKPROCESS)
    processSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_EVENT_ON_TRANSPORT_OPEN, openTransportInfo.name))
def CloseServerTransport(nextMessage : NetworkProcessMessage):
    global networkServer
    if not networkServer:
        Log(f"Network Server doesnt exist while trying to close server transport {nextMessage.data}",
            LOG_NETWORKPROCESS)
        return
    closeTransportInfo: NetworkUpdateTransport = nextMessage.data
    if closeTransportInfo.name not in networkServer.transportHandlers:
        Log(f"STransport doesnt exist while trying to close transport {nextMessage.data}", LOG_NETWORKPROCESS)
        return
    networkServer.Close(closeTransportInfo.name)
    Log(f"STransport Closed {closeTransportInfo.name} on ipandport={closeTransportInfo.ipandport}", LOG_NETWORKPROCESS)

def ConnectClientTransport(nextMessage : NetworkProcessMessage):
    global networkClient
    openTransportInfo: NetworkUpdateTransport = nextMessage.data
    if not networkClient:
        networkClient = NetworkClientBase()
    try:
        networkClient.Connect(openTransportInfo.name, openTransportInfo.transport(), openTransportInfo.ipandport)
    except Exception as e:
        Log(f"Failed to open transport {openTransportInfo.name} on ipandport={openTransportInfo.ipandport}, error: {e}",
            LOG_NETWORKPROCESS)
        processSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_CONNECT_FAIL, nextMessage.data))
        networkClient.Close(openTransportInfo.name)
        return

    networkClient.transportHandlers[openTransportInfo.name].onDisconnect.append(NetworkConnectionLost(openTransportInfo.name))
    processSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_CONNECT_SUCCESS, nextMessage.data))
    Log(f"CTransport Opened {openTransportInfo.name} on ipandport={openTransportInfo.ipandport}", LOG_NETWORKPROCESS)
def CloseClientTransport(nextMessage : NetworkProcessMessage, disconnectReason=NET_USER_DISCONNECTED):
    if not networkClient:
        Log(f"CNetwork Server doesnt exist while trying to close server transport {nextMessage.data}",
            LOG_NETWORKPROCESS)
        return
    closeTransportInfo: NetworkUpdateTransport = nextMessage.data
    if closeTransportInfo.name not in networkClient.transportHandlers:
        Log(f"CTransport doesnt exist while trying to close transport {nextMessage.data}", LOG_NETWORKPROCESS)
        return
    networkClient.Close(closeTransportInfo.name)
    processSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_DISCONNECT, NetworkDisconnect(disconnectReason,
                                                                                                    closeTransportInfo.name)))

def NetworkClientConnect(connection : ClientConnectionBase):
    global connections
    connections[connection.referenceId] = connection
    processSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_CLIENT_CONNECT,
                                                   NetworkConnectionStatus(connection.referenceId,
                                                                           True, connection.nickname)))
    Log(f"New client connection: {connection.referenceId}", LOG_NETWORKPROCESS)
def NetworkClientDisconnect(connection : ClientConnectionBase):
    global connections
    connections.pop(connection.referenceId)
    processSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_CLIENT_DISCONNECT,
                                                   NetworkConnectionStatus(connection.referenceId,
                                                                           False, connection.nickname)))
    Log(f"Client disconnected: {connection.referenceId}", LOG_NETWORKPROCESS)

def NetworkConnectionLost(transportName : str):
    def _ConnectionLost():
        CloseClientTransport(NetworkProcessMessage(NET_PROCESS_CLOSE_CLIENT_TRANSPORT,
                                                   NetworkUpdateTransport(transportName, None, None)),
                             NET_CONNECTION_LOST)
        processSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_DISCONNECT, NetworkDisconnect(NET_CONNECTION_LOST,
                                                                                                 transportName)))

    return _ConnectionLost

def NetworkProcessReceiveThread():
    global networkServer, networkClient, active, processSocket

    Log("NetworkProcessReceiveThread Started", LOG_NETWORKPROCESS)
    while active:
        if networkServer:
            nextMessageBytes = 1
            while nextMessageBytes:
                nextMessageBytes = networkServer.GetNextMessage()
                if nextMessageBytes:
                    nextMessage = NetworkEventFromBytes(nextMessageBytes[0])
                    nextMessage.processAs = NET_HOST
                    nextMessage.sender = nextMessageBytes[1].referenceId

                    processSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_RECEIVE_MESSAGE, nextMessage))

        if networkClient:
            nextMessageBytes = 1
            while nextMessageBytes:
                nextMessageBytes = networkClient.GetNextMessage()
                if nextMessageBytes:
                    nextMessage = NetworkEventFromBytes(nextMessageBytes[0])
                    nextMessage.processAs = NET_CLIENT
                    processSocket.send_pyobj(NetworkProcessMessage(NET_PROCESS_RECEIVE_MESSAGE, nextMessage))
