from engine.ecs import Component
import random, time

class GeneratorComponent(Component):
    def __init__(self):
        super().__init__()
        self.itemID = random.randint(0,8)
        self.lastCreatedItem = time.time()
        self.spawnTimer = 1