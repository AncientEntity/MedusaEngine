from engine.ecs import EntitySystem, Scene, Component
from engine.systems.renderer import SpriteRenderer


class NPCComponent(Component):
    def __init__(self):
        super().__init__()
        self.idleAnim = None
        self.runAnim = None
        self.speed = 50
        self.behaviourTick = None #Function that takes in a NPCComponent

class NPCSystem(EntitySystem):
    def __init__(self):
        super().__init__([NPCComponent])
    def Update(self, currentScene: Scene):
        for npc in currentScene.components[NPCComponent]:
            npc.behaviourTick(npc)