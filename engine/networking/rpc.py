from collections import namedtuple

from engine.ecs import EntitySystem
from engine.networking.networkstate import NetworkState

class RPCNotInEntitySystemError(Exception):
    pass

RPCAction = namedtuple('RPCAction', ['systemType', 'funcName', 'args'])


def RPC(func):
    def wrapper(*args, isCaller=True):
        if isCaller and NetworkState.identity:
            parentComponent = args[0]
            if not isinstance(parentComponent, EntitySystem):
                raise RPCNotInEntitySystemError()  # RPC Must be in a entity system.

            # todo serialize args
            # todo send over network

            func(*args[1:])
        else:

            # todo deserialize args

            func(*args[1:])


    return wrapper

if __name__ == "__main__":
    class Test(EntitySystem):
        @RPC
        def test(t1,t2):
            print(t1,t2)

    Test().test("T1","T2")