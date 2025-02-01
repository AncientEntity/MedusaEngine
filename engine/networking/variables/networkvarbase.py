from engine.logging import Log


class NetworkVarBase:
    def __init__(self):
        self._modified = False


    # Get/Set/Add as intended values
    def Set(self, value, modified=True):
        self._modified = modified
    def Add(self, value, modified=True):
        self._modified = modified
    def Get(self):
        pass


    # Serialized Get/Setters. Used for sending over network
    def SetFromBytes(self, byteValue, modified=True):
        self._modified = modified
    def GetAsBytes(self):
        pass