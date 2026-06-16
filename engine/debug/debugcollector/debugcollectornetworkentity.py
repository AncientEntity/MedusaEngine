from engine.debug.debugcollector.debugcollector import DebugCollector
from engine.ecs import Scene, Entity, NetworkEntity
from engine.engine import Engine
from engine.input import Input
from engine.tools.math import Distance


class DebugCollectorNetworkEntity(DebugCollector):
    def __init__(self):
        pass

    def Collect(self, game : Engine, parentEntity : NetworkEntity, currentScene : Scene):
        dumps = []

        interPosition = [round(item, 2) for item in parentEntity.position]
        actualPosition = [round(item, 2) for item in parentEntity.get_exact_position()]

        dumps.append(f"ownerId: {parentEntity.ownerId}")
        dumps.append(f"interpPos: {interPosition}")
        dumps.append(f"actualPos: {actualPosition}")
        dumps.append(f"interpDistance: {Distance(parentEntity.position,parentEntity.get_exact_position())}")

        for variable in parentEntity.GetNetworkVariables():
            dumps.append(f"nvar: {variable[0]}={variable[1].Get()}")


        return dumps