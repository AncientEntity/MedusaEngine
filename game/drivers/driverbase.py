from engine.ecs import Scene
from game.components.actorcomponent import ActorComponent


class DriverBase:
    def __init__(self):
        self.inputs = {
            "up": None,
            "down": None,
            "left": None,
            "right": None,
            "attack1": None,
            "reload": None
        }
        self.targetPosition = (0,0)

    def Update(self, actor : ActorComponent, currentScene : Scene):
        pass