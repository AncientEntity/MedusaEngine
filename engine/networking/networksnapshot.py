from engine.constants import NET_SNAPSHOT_FULL, NET_SNAPSHOT_PARTIAL, NET_HOST
from engine.ecs import Scene, NetworkEntity
from engine.networking.networkstate import NetworkState
from engine.networking.rpc import RPCAction
from engine.networking.variables.networkvarbase import NetworkVarBase
from engine.networking.variables.networkvarint import NetworkVarInt
from engine.networking.variables.networkvarvector import NetworkVarVector


class NetworkEntitySnapshot:
    def __init__(self, networkId, ownerId, variables):
        self.networkId = networkId
        self.ownerId = ownerId
        self.prefabName = ""
        self.variables = variables

    # SERIALIZATION IMPORTANT
    # technically ToBytes and FromBytes doesnt give back a perfect conversion
    # at this time ToBytes expects variables of form (attr, NetworkVarBase)
    # but FromBytes fills variables list with form (attr, bytearray)

    def ToBytes(self):
        snapshotBytes = bytearray()
        snapshotBytes.extend(self.networkId.to_bytes(4, byteorder='big', signed=True))
        snapshotBytes.extend(self.ownerId.to_bytes(4, byteorder='big', signed=True))
        if self.prefabName:
            snapshotBytes.extend(len(self.prefabName).to_bytes(4, byteorder='big'))
            snapshotBytes.extend(self.prefabName.encode('utf-8'))
        else:
            snapshotBytes.extend((0).to_bytes(4, byteorder='big'))
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
        entitySnapshot.ownerId = int.from_bytes(bytes[4:8], byteorder='big', signed=True)
        prefabNameLength = int.from_bytes(bytes[8:12], byteorder='big')
        entitySnapshot.prefabName = bytes[12:12+prefabNameLength].decode('utf-8')
        currentByte = 12+prefabNameLength
        variableCount = int.from_bytes(bytes[currentByte:currentByte+4], byteorder='big')
        currentByte += 4
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
        self.rpcCalls = []
    def __str__(self):
        return f"NetworkSnapshot({self.snapshotType}), len(entities)={len(self.entities)}"

    @staticmethod
    def GenerateSnapshotFull(currentScene : Scene):
        snapshot = NetworkSnapshot(NET_SNAPSHOT_FULL)
        netEntity : NetworkEntity
        for netEntity in currentScene.networkedEntities.values():
            entitySnapshot = NetworkEntitySnapshot(netEntity.entityId, netEntity.ownerId, netEntity.GetNetworkVariables())
            entitySnapshot.prefabName = netEntity.prefabName
            snapshot.entities.append(entitySnapshot)

        snapshot.rpcCalls = NetworkState.rpcQueue

        return snapshot

    @staticmethod
    def GenerateSnapshotPartial(currentScene : Scene):
        snapshot = NetworkSnapshot(NET_SNAPSHOT_PARTIAL)
        netEntity : NetworkEntity
        for netEntity in currentScene.networkedEntities.values():
            if not NetworkState.identity == NET_HOST and NetworkState.clientId != netEntity.ownerId:
                continue

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
            entitySnapshot.prefabName = netEntity.prefabName
            snapshot.entities.append(entitySnapshot)

        snapshot.rpcCalls = NetworkState.rpcQueue

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
        snapshotBytes.extend(len(self.rpcCalls).to_bytes(4, byteorder='big'))
        rpc : RPCAction
        for rpc in self.rpcCalls:
            rpcBytes = rpc.ToBytes()
            snapshotBytes.extend(len(rpcBytes).to_bytes(4, byteorder='big'))
            snapshotBytes.extend(rpcBytes)

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
        rpcCount = int.from_bytes(snapshotBytes[currentByte:currentByte+4], byteorder='big')
        currentByte += 4
        for i in range(rpcCount):
            rpcLength = int.from_bytes(snapshotBytes[currentByte:currentByte+4], byteorder='big')
            currentByte += 4
            snapshot.rpcCalls.append(RPCAction.FromBytes(snapshotBytes[currentByte:currentByte+rpcLength]))
            currentByte += rpcLength

        return snapshot

if __name__ == '__main__':
    variables = []
    variables.append(("_position", NetworkVarVector((-12.29,3,5.234))))
    variables.append(("test", NetworkVarInt(100001)))

    t = NetworkEntitySnapshot(12, 69, variables)
    t.prefabName = "test_prefab_null"

    t2 = NetworkSnapshot(0)
    t2.entities.append(t)

    t2.rpcCalls.append(RPCAction('FakeSystem', 'FakeFunc', b"testing"))
    t2.rpcCalls.append(RPCAction('FakeS23423ystem', 'Fak234eFunc', b"tes234ting"))
    t2.rpcCalls.append(RPCAction('Fak3eSystem', 'FakeFu2332nc', b"test2222ing"))
    t2.rpcCalls.append(RPCAction('Fake33System', 'Fak22eFunc', b"testi23423ng"))

    snapBytes = t2.SnapshotToBytes()
    backSnap = NetworkSnapshot.SnapshotFromBytes(snapBytes)
    print(backSnap.entities[0].prefabName)
    for i in range(len(backSnap.rpcCalls)):
        print(backSnap.rpcCalls[i])