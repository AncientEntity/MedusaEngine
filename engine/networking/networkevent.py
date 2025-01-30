

class NetworkEvent:
    def __init__(self, eventId, data : bytearray):
        self.eventId : int = eventId
        self.data : bytearray = data
    def __str__(self):
        return f"NetworkEvent({self.eventId}, data: {self.data})"

def NetworkEventToBytes(networkEvent : NetworkEvent):
    byteArray = bytearray()
    byteArray.extend(networkEvent.eventId.to_bytes(4, "little"))
    byteArray.extend(networkEvent.data)
    return byteArray

def NetworkEventFromBytes(bytes : bytearray):
    return NetworkEvent(int.from_bytes(bytes[0:4],"little"), bytes[4:])

class NetworkEventCreateEntity:
    def __init__(self):
        pass

if __name__ == "__main__":
    testEvent = NetworkEvent(2334532, bytearray(b"test"))
    testEventAsBytes = NetworkEventToBytes(testEvent)
    testEventBack = NetworkEventFromBytes(testEventAsBytes)
    print(testEventAsBytes)
    stillEqual = testEvent.eventId == testEventBack.eventId and testEvent.data == testEventBack.data
    print(testEvent, testEventBack, stillEqual)
    if not stillEqual:
        raise Exception("Before and After test event are not equal")