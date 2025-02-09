from engine.constants import NET_NONE


class NetworkState:
    identity = NET_NONE
    clientId = -1

    # Server Events
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

    # todo net headless/dedicated servers without rendering