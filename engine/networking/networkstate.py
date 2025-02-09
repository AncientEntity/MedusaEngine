from engine.constants import NET_NONE


class NetworkState:
    identity = NET_NONE
    clientId = -1

    # Server Events
    onClientConnect = {} #func(clientId)
    onClientDisconnect = {} #func(clientId)

    # Client Events
    onConnectSuccess = {} #func()
    onConnectFail = {} # func()
    onDisconnect = {} # func() # todo net implement

    # RPCs
    rpcQueue = []

    @staticmethod
    def TriggerHook(hookList, args):
        if isinstance(hookList, dict):
            hookList = list(hookList.values())
        for hook in hookList:
            hook(*args)

    # todo net headless/dedicated servers without rendering