from engine.debug.debugcollector.debugcollector import DebugCollector
from engine.ecs import Scene, Entity
from engine.engine import Engine
import time

from engine.networking.networkstate import NetworkState


class DebugCollectorNetInfo(DebugCollector):
    def __init__(self):
        pass

    def Collect(self, game : Engine, parentEntity : Entity, currentScene : Scene):
        dumps = []

        dumps.append(f"NetIdentity={NetworkState.GetNetworkIdentityString()}")
        dumps.append(f"Client Init: {game.clientInitialized}")
        dumps.append(f"Player Count: {game.NetworkPlayerCount()}")

        # This value could technically be inaccurate, because it is when we send it to the network process and then
        # whatever the network process does isn't necessarily what we expect.
        # So if the client says it hasn't recv in a while, but server says it has sent. That could be why.
        dumps.append(f"Time Since Snapshot Sent: {round(time.time() - game._lastSnapshotTimeSent, 6)}s")

        dumps.append(f"Time Since Snapshot Recv: {round(time.time() - game._lastSnapshotTimeRecv, 6)}s")

        return dumps