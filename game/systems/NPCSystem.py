from engine.ecs import EntitySystem, Scene
from engine.systems.renderer import SpriteRenderer


class NPCComponent:
    def __init__(self):
        super().__init__()
        self.idleAnim = None
        self.runAnim = None
        self.speed = 85
        self.behaviourTick = None #Function that takes in a NPCComponent

class NPCSystem(EntitySystem):
    def __init__(self):
        super().__init__([NPCComponent])
    def Update(self, currentScene: Scene):
        for npc in currentScene.components[NPCComponent]:
            npc.behaviourTick(npc)