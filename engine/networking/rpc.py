from collections import namedtuple

from engine.constants import NET_HOST, NET_ALL, NET_CALLER
from engine.ecs import EntitySystem
from engine.networking.networkstate import NetworkState
import json

class RPCNotInEntitySystemError(Exception):
    pass

class RPCAction:
    def __init__(self, systemType, funcName, args):
        self.systemType : str = systemType
        self.funcName : str = funcName
        self.args : bytearray = args

    def __str__(self):
        return (f"{self.systemType, self.funcName, self.args}")

    def ToBytes(self):
        rpcBytes = bytearray()
        systemTypeBytes = self.systemType.encode('utf-8')
        funcNameBytes = self.funcName.encode('utf-8')
        rpcBytes.extend(len(systemTypeBytes).to_bytes(4, 'big'))
        rpcBytes.extend(systemTypeBytes)
        rpcBytes.extend(len(funcNameBytes).to_bytes(4, 'big'))
        rpcBytes.extend(funcNameBytes)
        rpcBytes.extend(len(self.args).to_bytes(4, 'big'))
        rpcBytes.extend(self.args)
        return rpcBytes

    @staticmethod
    def FromBytes(rpcBytes : bytearray):
        systemTypeLength = int.from_bytes(rpcBytes[0:4], 'big')
        systemType = rpcBytes[4:4+systemTypeLength].decode('utf-8')
        currentByte = 4+systemTypeLength

        funcNameLength = int.from_bytes(rpcBytes[currentByte:currentByte+4], 'big')
        currentByte += 4
        funcName = rpcBytes[currentByte:currentByte+funcNameLength].decode('utf-8')
        currentByte += funcNameLength

        argLength = int.from_bytes(rpcBytes[currentByte:currentByte+4], 'big')
        currentByte += 4
        argBytes = rpcBytes[currentByte:currentByte+argLength]
        return RPCAction(systemType, funcName, argBytes)

def RPC(serverAuthorityRequired=True, targetCallers=NET_ALL): #todo targetCallers doesnt work properly
    def decorator(func):
        def wrapper(*args, **kwargs):
            isCaller = kwargs['isCaller'] if 'isCaller' in kwargs else True

            if isCaller and NetworkState.identity:
                parentComponent = args[0]
                if not isinstance(parentComponent, EntitySystem):
                    raise RPCNotInEntitySystemError()  # RPC Must be in a entity system.

                callerOnly = targetCallers == NET_CALLER # If targetCallers is NET_CALLER, it's not really an RPC now is it.

                if not callerOnly:
                    NetworkState.rpcQueue.append(RPCAction(type(args[0]).__name__,
                                                           func.__name__,
                                                           json.dumps(args[1:]).encode('utf-8')))

                if targetCallers & NetworkState.identity or targetCallers & NET_CALLER: # This is inside a isCaller check so we dont need to check if its' caller again
                    func(*args)
            else:
                if targetCallers & NetworkState.identity:
                    args = json.loads(kwargs['argBytes'].decode('utf-8'))
                    func(kwargs['self'], *args)
                elif not NetworkState.identity:
                    func(*args)

        wrapper.__rpc__ = {'serverAuthorityRequired': serverAuthorityRequired}

        return wrapper

    return decorator

if __name__ == "__main__":
    class TestSystem(EntitySystem):

        @RPC
        def test(self, t1, t2):
            print(t1,t2)

    TestSystem().test("T1","T2")

    tAction = RPCAction("FakeSystem", "FakeFunc", b"aererergbcde")
    tActionBytes = tAction.ToBytes()
    back = RPCAction.FromBytes(tActionBytes)
    print(back)