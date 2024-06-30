from engine.ecs import Component
import random


class GeneratorComponent(Component):
    def __init__(self,targetItem):
        super().__init__()
        self.itemID = targetItem
        self.spawnTimer = 0.7
        self.lastCreatedItem = 0
        self.lastItem = None
        self.jammedParticles = None
