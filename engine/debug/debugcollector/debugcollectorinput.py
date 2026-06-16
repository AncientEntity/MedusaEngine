from engine.debug.debugcollector.debugcollector import DebugCollector
from engine.ecs import Scene, Entity
from engine.engine import Engine
from engine.input import Input


class DebugCollectorInput(DebugCollector):
    def __init__(self):
        pass

    def Collect(self, game : Engine, parentEntity : Entity, currentScene : Scene):
        return Input.DumpInputStates()