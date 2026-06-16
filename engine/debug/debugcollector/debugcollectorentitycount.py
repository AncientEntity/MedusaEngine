from engine.debug.debugcollector.debugcollector import DebugCollector
from engine.ecs import Scene, Entity
from engine.engine import Engine
import time

from engine.networking.networkstate import NetworkState


class DebugCollectorEntityCount(DebugCollector):
    def __init__(self):
        pass

    def Collect(self, game : Engine, parentEntity : Entity, currentScene : Scene):
        dumps = []

        dumps.append(f"Total Entities: {len(currentScene.entities)}, Network Entities: {len(currentScene.networkedEntities)}")

        ownerMap = {}

        for entity in currentScene.networkedEntities.values():
            if entity.ownerId not in ownerMap:
                ownerMap[entity.ownerId] = 1
            else:
                ownerMap[entity.ownerId] += 1

        for ownerId in sorted(ownerMap.keys()):
            dumps.append(f"Entities owned by {f"client{ownerId}" if ownerId >= 0 else f"server"}: {ownerMap[ownerId]}")

        #ownedEntities = sum(1 for entity in currentScene.networkedEntities.values() if entity.ownerId == NetworkState.clientId)
        #dumps.append(f"My Entities: {ownedEntities}")

        return dumps