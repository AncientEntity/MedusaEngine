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


if __name__ == "__main__":
    testEvent = NetworkEvent(2334532, bytearray(b"test"))
    testEventAsBytes = NetworkEventToBytes(testEvent)
    testEventBack = NetworkEventFromBytes(testEventAsBytes)
    print(testEventAsBytes)
    stillEqual = testEvent.eventId == testEventBack.eventId and testEvent.data == testEventBack.data
    print(testEvent, testEventBack, stillEqual)
    if not stillEqual:
        raise Exception("Before and After test event are not equal")
