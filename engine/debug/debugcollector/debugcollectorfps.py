from engine.debug.debugcollector.debugcollector import DebugCollector
from engine.ecs import Scene, Entity
from engine.engine import Engine


class DebugCollectorFPS(DebugCollector):
    def __init__(self):
        pass

    def Collect(self, game : Engine, parentEntity : Entity, currentScene : Scene):
        if game.deltaTime == 0:
            return ["FPS: Fastly"]
        else:
            return [f"FPS: {round(1.0 / game.deltaTime, 2)}"]