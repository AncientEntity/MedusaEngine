from engine.constants import NET_NONE, NET_LISTENSERVER, NET_HOST, NET_CLIENT


class NetworkState:
    identity = NET_NONE
    clientId = -1

    # Server Events
    serverOnTransportOpen = {} #func(transportName : str)
    onClientConnect = {} #func(clientId : int)
    onClientDisconnect = {} #func(clientId : int)

    # Client Events
    onConnectSuccess = {} #func()
    onConnectFail = {} # func()
    onDisconnect = {} # func(reason : str, transportName : str)

    # RPCs
    rpcQueue = []

    @staticmethod
    def TriggerHook(hookList, args):
        if isinstance(hookList, dict):
            hookList = list(hookList.values())
        for hook in hookList:
            hook(*args)

    @staticmethod
    def GetNetworkIdentityString():
        if NetworkState.identity == NET_NONE:
            return "None"
        elif NetworkState.identity == NET_LISTENSERVER:
            return "ListenServer"
        elif NetworkState.identity == NET_HOST:
            return "Host"
        elif NetworkState.identity == NET_CLIENT:
            return "Client"
        else:
            return "Unknown"