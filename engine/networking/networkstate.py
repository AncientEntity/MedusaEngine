from engine.constants import NET_NONE


class NetworkState:
    identity = NET_NONE
    clientId = -1

    processSocket = None

    # Server Events
    onClientConnect = [] #func(clientId)
    onClientDisconnect = [] #func(clientId)

    # Client Events
    onConnectSuccess = [] #func()
    onConnectFail = [] # func()

    @staticmethod
    def TriggerHook(hookList, args):
        for hook in hookList:
            hook(*args)