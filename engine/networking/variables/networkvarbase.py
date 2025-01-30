from engine.logging import Log


class NetworkVarBase:
    networkVariables : dict[int,list] = {}
    def __init__(self, entityId : int):
        self._modified = False
        self.entityId = entityId # Pass in entity id on creation, as long as entity is valid, it will update this.

        if entityId is not None:
            RegisterNetworkVariable(self)

    # Get/Set as intended values
    def Set(self, value, modified=True):
        self._modified = modified
    def Get(self):
        pass

    # Serialized Get/Setters. Used for sending over network
    def SetFromBytes(self, byteValue, modified=True):
        self._modified = modified
    def GetAsBytes(self):
        pass

def RegisterNetworkVariable(networkVariable : NetworkVarBase):
    if networkVariable.entityId not in NetworkVarBase.networkVariables:
        NetworkVarBase.networkVariables[networkVariable.entityId] = [networkVariable]
    else:
        NetworkVarBase.networkVariables[networkVariable.entityId].append(networkVariable)

def RemoveNetworkVariable(networkVariable : NetworkVarBase):
    if networkVariable.entityId in NetworkVarBase.networkVariables:
        NetworkVarBase.networkVariables[networkVariable.entityId].remove(networkVariable)
        if len(NetworkVarBase.networkVariables[networkVariable.entityId]) == 0:
            NetworkVarBase.networkVariables.pop(networkVariable.entityId)
        return
    else:
        Log("Failed to find network variable in network variables.")