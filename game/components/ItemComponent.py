from engine.ecs import Component


class ItemComponent(Component):
    def __init__(self,id):
        super().__init__()
        self.itemID = id
        self.worth = 1
        self.reappearTime = None
        self.reappearPosition = None
