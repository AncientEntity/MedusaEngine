from engine.ecs import Component


class ItemComponent(Component):
    def __init__(self,id):
        super().__init__()
        self.itemID = id
