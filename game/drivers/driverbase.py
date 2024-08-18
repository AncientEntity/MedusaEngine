from engine.ecs import Scene
from game.components.actorcomponent import ActorComponent


class DriverBase:
    def __init__(self):
        self.inputs = {
            "up": None,
            "down": None,
            "left": None,
            "right": None,
            "attack1": None
        }
        self.targetPosition = None

    def Update(self, actor : ActorComponent, currentScene : Scene):
        pass