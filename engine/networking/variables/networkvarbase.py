from engine.logging import Log


class NetworkVarBase:
    def __init__(self):
        self._modified = False
        self.hasAuthority = False
        self.prioritizeOwner = False # If true, the server's incoming values wont modify the owner's variable value

        self._hooks = [] # func(self) passes in self
        self._memoryView = None


    # Get/Set/Add as intended values
    def Set(self, value, modified=True):
        self._modified = modified
        self.TriggerHooks()
    def Add(self, value, modified=True):
        self._modified = modified
        self.TriggerHooks()
    def Get(self):
        pass


    # Serialized Get/Setters. Used for sending over network
    def SetFromBytes(self, byteValue, modified=True):
        self._modified = modified
        self.TriggerHooks()
        self._memoryView = memoryview(byteValue)

    def GetAsBytes(self):
        pass

    def AreBytesEqual(self, otherBytes : bytearray):
        return memoryview(otherBytes) == self._memoryView

    def AddHook(self, func, triggerOnAdd=False):
        self._hooks.append(func)
        if triggerOnAdd:
            func(self)
    def TriggerHooks(self):
        for func in self._hooks:
            func(self)

    def __str__(self):
        return f"{str(type(self))}(value={self.Get()})"