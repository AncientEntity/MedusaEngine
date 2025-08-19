import socket
import threading
import lzma


from engine.constants import NET_NONE, NET_CLIENT, NET_HOST
from engine.logging import Log, LOG_WARNINGS, LOG_ERRORS
from engine.networking.connections.clientconnectionbase import ClientConnectionBase
from engine.networking.connections.clientconnectionsocket import ClientConnectionSocket
from engine.networking.transport.networktransportbase import NetworkTransportBase
import time

# NetworkUDPTransport is EXPERIMENTAL WITH SOME INEVITABLE ISSUES LISTED AS TODOS A LITTLE LOWER.
# INFO ON MESSAGES
# Each message is sent like ID+MESSAGE(optional)
# as in:
# - MSGMessage : Message for game.
# - ENDNone    : End
# - HTBNone    : Heartbeat
# IMPORTANT TODOS:
# todo - snapshots over 65536 compressed will error (gracefully within try/catch).
# todo   Need to break messages up when too big, like into 4096 byte fragments, and handle fragmenting...
class NetworkUDPTransport(NetworkTransportBase):
    def __init__(self):
        super().__init__()
        self._socket : socket.socket = None

        self.heartbeatDelay = 8
        self.maxMissedHeartbeats = 3

        self.targetServer : (str,int) = None

        self.active = True
        self._role = NET_NONE

        self._serverIp = None
        self._activeAddresses = [] # Ip and port tuples
        self._kickedIPs = [] # Resets in Close()

        self.activeConnectionsDict = {}

        self.heartbeatThread = None

    def Connect(self, targetServer : (str, int)):
        if self._role != NET_NONE:
            Log(f"NetworkUDPTransport already being used. Role: {self._role}", LOG_ERRORS if self._role == NET_HOST else LOG_WARNINGS)
            return

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._serverIp = targetServer

        self.heartbeatThread = threading.Thread(target=self.ClientHeartbeat, args=())
        self.heartbeatThread.start()

        self._role = NET_CLIENT
        self.active = True

    def Open(self, ip : str, port : int):
        if self._role != NET_NONE:
            Log(f"NetworkUDPTransport already being used. Role: {self._role}", LOG_ERRORS if self._role == NET_CLIENT else LOG_WARNINGS)
            return

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((ip, port))

        self.heartbeatThread = threading.Thread(target=self.ServerHeartbeat, args=())
        self.heartbeatThread.start()

        self.active = True
        self._role = NET_HOST
    def Close(self):
        if self._role == NET_NONE:
            Log(f"NetworkUDPTransport already inactive.", LOG_WARNINGS)

        if self._role == NET_CLIENT:
            self._socket.sendto(b"END", self._serverIp)

        self._kickedIPs = []
        self.clientConnections = []
        self.activeConnectionsDict = []

        self._socket.close()
        self._socket = None
        self.active = False
        self._role = NET_NONE
        self._serverIp = None


    # UDP Kick will essentially block the IP until the NetworkUDPTransport restarts.
    def Kick(self, clientConnection : ClientConnectionBase):
        if self._role != NET_HOST:
            Log(f"NetworkUDPTransport cannot kick with role: {self._role}", LOG_WARNINGS)
            return

        if clientConnection in self.clientConnections: # can assume clientConnection is ClientConnectionSocket.
            self._kickedIPs.append(clientConnection.address[0])
            self.DisconnectClient(clientConnection.address)
            Log(f"NetworkUDPTransport has kicked: {clientConnection.address[0]}")

    # todo implement a SendAll into NetworkTransportBase and here so we only compress one time...
    def Send(self, message, clientConnection : ClientConnectionSocket):
        # For udp, if someone disconnects but we dont know yet it slows this down, slowing the server down.
        # So for those who missed a heartbeat we dont send anything...
        if self._role == NET_HOST and time.time() - clientConnection.udpHeartbeat > self.heartbeatDelay:
            return

        msgCompressed = lzma.compress(b"MSG"+message)
        if len(msgCompressed) > 65536:
            Log(f"msgCompressed exceeds the max size of 65536. Size: {len(msgCompressed)}")
        if self._role == NET_HOST and clientConnection:
            self._socket.sendto(msgCompressed, clientConnection.address)
        elif self._role == NET_CLIENT:
            self._socket.sendto(msgCompressed, self._serverIp)

    def ClientHeartbeat(self):
        while self.active:
            self._socket.sendto(lzma.compress(b"HTB"), self._serverIp)
            time.sleep(self.heartbeatDelay)

    def ServerHeartbeat(self):
        while self.active:
            client : ClientConnectionSocket
            for client in self.clientConnections:
                if time.time() - client.udpHeartbeat > self.heartbeatDelay*self.maxMissedHeartbeats:
                    self.DisconnectClient(client.address)
                    Log(f"Client({client.nickname}) missed {self.maxMissedHeartbeats} heartbeats, assuming connection closed.")
            time.sleep(self.heartbeatDelay / 2.0) # magic number I know but c'mon

    def Receive(self, buffer=8192) -> tuple[bytes, ClientConnectionBase]:

        try:
            message, addrMsg = self._socket.recvfrom(buffer)
            message = lzma.decompress(message)
        except ConnectionResetError as e:
            return None
        except Exception as e:
            Log(f"Error raised within Receive() or NetworkUDPTransport {e}", LOG_WARNINGS) # todo better handling
            return None

        if addrMsg[0] in self._kickedIPs:
            return None


        if self._role == NET_HOST:
            if addrMsg not in self._activeAddresses:
                self._activeAddresses.append(addrMsg)
                clientConnection = ClientConnectionSocket(*addrMsg)
                self.activeConnectionsDict[addrMsg] = clientConnection
                self.clientConnections.append(clientConnection)
                self.CallHook(self.onClientConnect, (clientConnection,))
            else:
                clientConnection = self.activeConnectionsDict[addrMsg]
                if message.startswith(b"END"): # Disconnect
                    self.DisconnectClient(addrMsg)
                    return None
                clientConnection.udpHeartbeat = time.time()

        elif self._role == NET_CLIENT:
            clientConnection = None

        if message.startswith(b"MSG"):
            return (message[3:], clientConnection) # only pass [3:] to ignore "MSG" at start.
        return None

    def DisconnectClient(self, addrMsg):
        clientConnection = self.activeConnectionsDict[addrMsg]

        self.activeConnectionsDict.pop(clientConnection.address)
        self.clientConnections.remove(clientConnection)
        clientConnection.active = False
        self.CallHook(self.onClientDisconnect, (clientConnection,))

    def CallHook(self, hookArray, args):
        for hook in hookArray:
            hook(*args)