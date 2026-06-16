from engine.constants import NET_NONE, NET_HOST
from engine.logging import Log
from engine.networking.networkstate import NetworkState


class NetworkVarBase:
    def __init__(self):
        self._modified = False
        self.hasAuthority = False

        self.serverAuthorityRequired = False

        self._hooks = [] # func(self) passes in self
        self._bytesValue : bytearray = b""


    # Get/Set/Add as intended values
    def Set(self, value, modified=True):
        if self.hasAuthority:
            self._modified = modified

        self.TriggerHooks()
        self._bytesValue = self.GetAsBytes()
    def Add(self, value, modified=True):
        if self.hasAuthority: # only update locally if you dont have authority.
            self._modified = modified

        self.TriggerHooks()
        self._bytesValue = self.GetAsBytes()
    def Get(self):
        pass


    # Serialized Get/Setters. Used for sending over network
    def SetFromBytes(self, byteValue, modified=True):
        self._modified = modified
        self.TriggerHooks()
        self._bytesValue = byteValue

    def GetAsBytes(self):
        pass

    def AreBytesEqual(self, otherBytes : bytearray):
        return otherBytes == self._bytesValue

    def AddHook(self, func, triggerOnAdd=False):
        self._hooks.append(func)
        if triggerOnAdd:
            func(self)
    def TriggerHooks(self):
        for func in self._hooks:
            func(self)

    def __str__(self):
        return f"{str(type(self))}(value={self.Get()})"