import multiprocessing, threading, time
from collections import namedtuple

from engine.constants import NET_PROCESS_SHUTDOWN, NET_PROCESS_OPEN_SERVER_TRANSPORT, \
    NET_PROCESS_CLOSE_SERVER_TRANSPORT, NET_PROCESS_CONNECT_CLIENT_TRANSPORT, NET_PROCESS_CLOSE_CLIENT_TRANSPORT, \
    NET_PROCESS_CLIENT_SEND_MESSAGE, NET_PROCESS_SERVER_SEND_MESSAGE, NET_CLIENT, NET_PROCESS_RECEIVE_MESSAGE, NET_HOST
from engine.logging import Log, LOG_NETWORKING
from engine.networking.connections.clientconnectionbase import ClientConnectionBase
from engine.networking.networkclientbase import NetworkClientBase
from engine.networking.networkevent import NetworkEventFromBytes
from engine.networking.networkserverbase import NetworkServerBase

# id is from constants.py NET_PROCESS_*
# data is whatever data is required.
#NetworkProcessMessage = namedtuple('NetworkProcessMessage', ['id', 'data'])
class NetworkProcessMessage:
    def __init__(self, id, data):
        self.id : int = id
        self.data = data
        self.requestMade : float = time.time()

NetworkUpdateTransport = namedtuple('NetworkUpdateTransport', ['name', 'transport', 'ipandport'])

NetworkSendMessage = namedtuple('NetworkSendMessage', ['transportName', 'target', 'msgBytes'])

active = True
networkServer: NetworkServerBase = None
networkClient: NetworkClientBase = None
connections = {}

def NetworkProcessMain(inQueue : multiprocessing.Queue, outQueue : multiprocessing.Queue):
    global networkServer, networkClient, active, connections
    #todo log files should have a different prefix set like log-net-* right now 2 files are generated.
    Log("Network Process Main Started", LOG_NETWORKING)

    receiveThread = threading.Thread(target=NetworkProcessReceiveThread, args=(outQueue,))
    receiveThread.start()

    active = True
    lastMessageStart = time.time()
    t = 0
    while active:
        nextMessage : NetworkProcessMessage = inQueue.get()

        curTime = time.time()
        timeDiff = curTime - lastMessageStart
        t += 1
        if t % 20 == 0:
            print(f"Process Delay: {time.time() - nextMessage.requestMade}, queuelen: {inQueue.qsize()}, delay between: {timeDiff}, pps: {1.0 / timeDiff if timeDiff != 0 else 0}, t: {t}")
        lastMessageStart = curTime

        if nextMessage.id == NET_PROCESS_SHUTDOWN:
            active = False

            if networkServer:
                for layer in list(networkServer.transportHandlers.keys()):
                    networkServer.Close(layer)
            if networkClient:
                for layer in list(networkClient.transportHandlers.keys()):
                    networkClient.Close(layer)

            inQueue.close()
            outQueue.close()
            Log("Network Process Main Shutdown")
            exit(0)

        # open close server transport
        elif nextMessage.id == NET_PROCESS_OPEN_SERVER_TRANSPORT:
            openTransportInfo : NetworkUpdateTransport = nextMessage.data
            if not networkServer:
                networkServer = NetworkServerBase()
            networkServer.Open(openTransportInfo.name, openTransportInfo.transport(), openTransportInfo.ipandport)
            networkServer.transportHandlers[openTransportInfo.name].onClientConnect.append(NetworkClientConnect)
            networkServer.transportHandlers[openTransportInfo.name].onClientDisconnect.append(NetworkClientDisconnect)
            Log(f"Transport Opened {openTransportInfo.name} on ipandport={openTransportInfo.ipandport}", LOG_NETWORKING)
        elif nextMessage.id == NET_PROCESS_CLOSE_SERVER_TRANSPORT:
            if not networkServer:
                Log(f"Network Server doesnt exist while trying to close server transport {nextMessage.data}", LOG_NETWORKING)
                continue
            closeTransportInfo : NetworkUpdateTransport = nextMessage.data
            if closeTransportInfo.name not in networkServer.transportHandlers:
                Log(f"STransport doesnt exist while trying to close transport {nextMessage.data}", LOG_NETWORKING)
                continue
            networkServer.Close(closeTransportInfo.name)
            Log(f"STransport Closed {openTransportInfo.name} on ipandport={openTransportInfo.ipandport}", LOG_NETWORKING)

        # connect / close client transport
        elif nextMessage.id == NET_PROCESS_CONNECT_CLIENT_TRANSPORT:
            openTransportInfo : NetworkUpdateTransport = nextMessage.data
            if not networkClient:
                networkClient = NetworkClientBase()
            networkClient.Connect(openTransportInfo.name, openTransportInfo.transport(), openTransportInfo.ipandport)
            Log(f"Transport Opened {openTransportInfo.name} on ipandport={openTransportInfo.ipandport}", LOG_NETWORKING)
        elif nextMessage.id == NET_PROCESS_CLOSE_CLIENT_TRANSPORT:
            if not networkClient:
                Log(f"CNetwork Server doesnt exist while trying to close server transport {nextMessage.data}", LOG_NETWORKING)
                continue
            closeTransportInfo : NetworkUpdateTransport = nextMessage.data
            if closeTransportInfo.name not in networkClient.transportHandlers:
                Log(f"CTransport doesnt exist while trying to close transport {nextMessage.data}", LOG_NETWORKING)
                continue
            networkClient.Close(closeTransportInfo.name)

        # send messages
        elif nextMessage.id == NET_PROCESS_CLIENT_SEND_MESSAGE:
            sendMessageInfo : NetworkSendMessage = nextMessage.data
            networkClient.Send(sendMessageInfo.msgBytes, sendMessageInfo.transportName)

        elif nextMessage.id == NET_PROCESS_SERVER_SEND_MESSAGE:
            sendMessageInfo : NetworkSendMessage = nextMessage.data
            if not sendMessageInfo.target:
                networkServer.SendAll(sendMessageInfo.msgBytes, sendMessageInfo.transportName)
            else:
                networkServer.Send(sendMessageInfo.msgBytes, connections[sendMessageInfo.target], sendMessageInfo.transportName)

def NetworkClientConnect(connection : ClientConnectionBase):
    global connections
    connections[connection.referenceId] = connection
    Log(f"New client connection: {connection.referenceId}")
def NetworkClientDisconnect(connection : ClientConnectionBase):
    global connections
    connections.pop(connection.referenceId)
    Log(f"Client disconnected: {connection.referenceId}")

def NetworkProcessReceiveThread(outQueue : multiprocessing.Queue):
    global networkServer, networkClient, active

    Log("NetworkProcessReceiveThread Started", LOG_NETWORKING)
    while active:
        if networkServer:
            nextMessageBytes = 1
            while nextMessageBytes:
                nextMessageBytes = networkServer.GetNextMessage()
                if nextMessageBytes:
                    nextMessage = NetworkEventFromBytes(nextMessageBytes[0])
                    nextMessage.processAs = NET_HOST
                    nextMessage.sender = nextMessageBytes[1].referenceId

                    outQueue.put(NetworkProcessMessage(NET_PROCESS_RECEIVE_MESSAGE, nextMessage))

        if networkClient:
            nextMessageBytes = 1
            while nextMessageBytes:
                nextMessageBytes = networkClient.GetNextMessage()
                if nextMessageBytes:
                    nextMessage = NetworkEventFromBytes(nextMessageBytes[0])
                    nextMessage.processAs = NET_CLIENT
                    outQueue.put(NetworkProcessMessage(NET_PROCESS_RECEIVE_MESSAGE, nextMessage))
