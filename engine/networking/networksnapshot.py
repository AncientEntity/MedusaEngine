from engine.constants import NET_SNAPSHOT_FULL, NET_SNAPSHOT_PARTIAL
from engine.ecs import Scene, NetworkEntity
from engine.networking.variables.networkvarbase import NetworkVarBase
from engine.networking.variables.networkvarint import NetworkVarInt
from engine.networking.variables.networkvarvector import NetworkVarVector


class NetworkEntitySnapshot:
    def __init__(self, networkId, ownerId, variables):
        self.networkId = networkId
        self.ownerId = ownerId
        self.variables = variables

    # SERIALIZATION IMPORTANT
    # technically ToBytes and FromBytes doesnt give back a perfect conversion
    # at this time ToBytes expects variables of form (attr, NetworkVarBase)
    # but FromBytes fills variables list with form (attr, bytearray)

    def ToBytes(self):
        snapshotBytes = bytearray()
        snapshotBytes.extend(self.networkId.to_bytes(4, byteorder='big', signed=True))
        snapshotBytes.extend(self.ownerId.to_bytes(4, byteorder='big'))
        snapshotBytes.extend(len(self.variables).to_bytes(4, byteorder='big'))
        for variable in self.variables:
            snapshotBytes.extend(len(variable[0]).to_bytes(4, byteorder='big'))
            snapshotBytes.extend(variable[0].encode('utf-8'))
            data = variable[1].GetAsBytes()
            snapshotBytes.extend(len(data).to_bytes(4, byteorder='big'))
            snapshotBytes.extend(data)

        return snapshotBytes


    @staticmethod
    def FromBytes(bytes : bytearray):
        entitySnapshot = NetworkEntitySnapshot(0,0,[])
        entitySnapshot.networkId = int.from_bytes(bytes[0:4], byteorder='big', signed=True)
        entitySnapshot.ownerId = int.from_bytes(bytes[4:8], byteorder='big')
        variableCount = int.from_bytes(bytes[8:12], byteorder='big')
        currentByte = 12
        for i in range(variableCount):
            nameSize = int.from_bytes(bytes[currentByte:currentByte+4], byteorder='big')
            currentByte += 4
            variableName = bytes[currentByte:currentByte+nameSize].decode('utf-8', errors='ignore')
            currentByte += nameSize
            dataSize = int.from_bytes(bytes[currentByte:currentByte+4], byteorder='big')
            currentByte += 4
            entitySnapshot.variables.append((variableName, bytes[currentByte:currentByte+dataSize]))
            currentByte += dataSize

        return entitySnapshot


class NetworkSnapshot:
    def __init__(self, snapshotType):
        self.snapshotType = snapshotType # NET_SNAPSHOT_PARTIAL or NET_SNAPSHOT_FULL
        self.entities = []
    def __str__(self):
        return f"NetworkSnapshot({self.snapshotType}), len(entities)={len(self.entities)}"

    @staticmethod
    def GenerateSnapshotFull(currentScene : Scene):
        snapshot = NetworkSnapshot(NET_SNAPSHOT_FULL)
        netEntity : NetworkEntity
        for netEntity in currentScene.networkedEntities:
            entitySnapshot = NetworkEntitySnapshot(netEntity.entityId, netEntity.ownerId, netEntity.GetNetworkVariables())
            snapshot.entities.append(entitySnapshot)
        return snapshot

    @staticmethod
    def GenerateSnapshotPartial(currentScene : Scene):
        snapshot = NetworkSnapshot(NET_SNAPSHOT_PARTIAL)
        netEntity : NetworkEntity
        for netEntity in currentScene.networkedEntities:
            if netEntity.entityId:
                variablesToUpdate = []
                variable : NetworkVarBase
                for variable in netEntity.GetNetworkVariables():
                    if variable[1]._modified:
                        variablesToUpdate.append(variable)
                    variable[1]._modified = False #todo not sure if this needs to be here or not
                if len(variablesToUpdate) == 0:
                    continue # no need to include in snapshot

            entitySnapshot = NetworkEntitySnapshot(netEntity.entityId, netEntity.ownerId, variablesToUpdate)
            snapshot.entities.append(entitySnapshot)
        return snapshot

    def SnapshotToBytes(self):
        snapshotBytes = bytearray()
        snapshotBytes.extend(self.snapshotType.to_bytes(4, byteorder='big'))
        snapshotBytes.extend(len(self.entities).to_bytes(4, byteorder='big'))
        entity : NetworkEntitySnapshot
        for entity in self.entities:
            entityBytes = entity.ToBytes()
            snapshotBytes.extend(len(entityBytes).to_bytes(4, byteorder='big'))
            snapshotBytes.extend(entityBytes)

        return snapshotBytes

    @staticmethod
    def SnapshotFromBytes(snapshotBytes : bytearray):
        snapshot = NetworkSnapshot(int.from_bytes(snapshotBytes[0:4], byteorder='big'))
        entityCount = int.from_bytes(snapshotBytes[4:8], byteorder='big')
        currentByte = 8
        for i in range(entityCount):
            entityByteSize = int.from_bytes(snapshotBytes[currentByte:currentByte+4],byteorder='big')
            currentByte += 4
            entity = NetworkEntitySnapshot.FromBytes(snapshotBytes[currentByte:currentByte+entityByteSize])
            currentByte += entityByteSize
            snapshot.entities.append(entity)


        return snapshot

if __name__ == '__main__':
    variables = []
    variables.append(("_position", NetworkVarVector(12, (-12.29,3,5.234))))
    variables.append(("test", NetworkVarInt(60, 100001)))

    t = NetworkEntitySnapshot(12, 69, variables)

    t2 = NetworkSnapshot(0)
    t2.entities.append(t)

    snapBytes = t2.SnapshotToBytes()
    backSnap = NetworkSnapshot.SnapshotFromBytes(snapBytes)