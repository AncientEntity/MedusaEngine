from engine.ecs import Component

class ItemComponent(Component):
    def __init__(self):
        super().__init__()
        self.held = False
        self.spriteRotationOffset = 0