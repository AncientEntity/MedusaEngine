from engine.constants import NET_NONE


class NetworkState:
    identity = NET_NONE
    clientId = -1

    # Server Events
    onClientConnect = [] #func(clientId)
    onClientDisconnect = [] #func(clientId)

    # Client Events
    # None currently implemented


    @staticmethod
    def TriggerHook(hookList, args):
        for hook in hookList:
            hook(*args)