from engine.constants import NET_NONE
from engine.networking.connections.clientconnectionbase import ClientConnectionBase
from engine.networking.variables.networkvarvector import NetworkVarVector

# Used for conversions in NetworkEventCreateEntity and possibly other places.
vectorForConversions = NetworkVarVector((0,0))

class NetworkEvent:
    def __init__(self, eventId, data : bytearray):
        self.eventId : int = eventId
        self.data : bytearray = data

        # not serialized
        self.processAs = NET_NONE # NET_NONE or NET_CLIENT or NET_HOST or NET_LISTENSERVER
        self.sender : ClientConnectionBase = None
    def __str__(self):
        return f"NetworkEvent({self.eventId}, data: {self.data}, processAs: {self.processAs})"

def NetworkEventToBytes(networkEvent : NetworkEvent):
    byteArray = bytearray()
    byteArray.extend(networkEvent.eventId.to_bytes(4, "little"))
    byteArray.extend(networkEvent.data)
    return byteArray

def NetworkEventFromBytes(bytes : bytearray):
    return NetworkEvent(int.from_bytes(bytes[0:4],"little"), bytes[4:])

class NetworkEventCreateEntity: #todo probably remove
    def __init__(self, prefab_name, position):
        self.prefab_name : str = prefab_name
        self.position : str = position
    def ToBytes(self):
        byteArray = bytearray()
        # name
        nameAsBytes = self.prefab_name.encode('utf-8')
        byteArray.extend(len(nameAsBytes).to_bytes(4,"little"))
        byteArray.extend(nameAsBytes)
        # position
        vectorForConversions.Set(self.position)
        vectorAsBytes = vectorForConversions.GetAsBytes()
        byteArray.extend(len(vectorAsBytes).to_bytes(4,"little"))
        byteArray.extend(vectorAsBytes)

        return byteArray
    @staticmethod
    def FromBytes(byteArray : bytearray):
        nameSize = int.from_bytes(byteArray[0:4],"little")
        positionSize = int.from_bytes(byteArray[4+nameSize:8+nameSize],"little")
        vectorForConversions.SetFromBytes(byteArray[8+nameSize:8+nameSize+positionSize])
        return NetworkEventCreateEntity(byteArray[4:4+nameSize].decode(), vectorForConversions.Get())



if __name__ == "__main__":
    testEvent = NetworkEvent(2334532, bytearray(b"test"))
    testEventAsBytes = NetworkEventToBytes(testEvent)
    testEventBack = NetworkEventFromBytes(testEventAsBytes)
    print(testEventAsBytes)
    stillEqual = testEvent.eventId == testEventBack.eventId and testEvent.data == testEventBack.data
    print(testEvent, testEventBack, stillEqual)
    if not stillEqual:
        raise Exception("Before and After test event are not equal")

    testCreateEntity = NetworkEventCreateEntity("test", (-1.523,10324.2))
    print(testCreateEntity.prefab_name, testCreateEntity.position)
    testCreateEntityBytes = testCreateEntity.ToBytes()
    testCreateEntity = NetworkEventCreateEntity.FromBytes(testCreateEntityBytes)
    print(testCreateEntity.prefab_name, testCreateEntity.position)
