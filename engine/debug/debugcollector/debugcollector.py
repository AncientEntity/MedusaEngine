from engine.ecs import Scene, Entity
from engine.engine import Engine
import random

class DebugCollector:
    def __init__(self):
        pass

    def Collect(self, game : Engine, parentEntity : Entity, currentScene : Scene):
        return [f"Default Debug Collector {random.randint(-10000,10000)}"]