from engine.ecs import Component

class ConsumerComponent(Component):
    def __init__(self,wantedItem):
        super().__init__()
        self.itemID = wantedItem
