from engine.constants import NET_ALL, NET_NONE
from engine.networking.networkstate import NetworkState
from engine.tools.platform import IsPlatformWeb


# todo experiment with putting this decorator into @RPC, to catch any weird issues with RPCs running on wrong host/clients.
def StateAssert(targetCallers=NET_ALL, ignoreWhenNoNetworkIdentity=True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            assert (NetworkState.identity & targetCallers) or (ignoreWhenNoNetworkIdentity and NetworkState.identity == NET_NONE)
            return func(*args, **kwargs)

        return wrapper

    return decorator
