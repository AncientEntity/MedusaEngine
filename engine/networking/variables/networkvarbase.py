from engine.logging import Log


class NetworkVarBase:
    def __init__(self):
        self._modified = False
        self.hasAuthority = False

        self._hooks = [] # func(self) passes in self


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
    def GetAsBytes(self):
        pass

    def AddHook(self, func):
        self._hooks.append(func)
    def TriggerHooks(self):
        for func in self._hooks:
            func(self)