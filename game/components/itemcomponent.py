from engine.ecs import Component

class ItemComponent(Component):
    def __init__(self, itemID):
        super().__init__()
        self.itemID = itemID
        self.weapon = True # If true it will replace the held item... hopefully there is an action?
        self.action = None # Function