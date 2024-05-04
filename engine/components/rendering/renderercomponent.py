from engine.ecs import Component

class RendererComponent(Component):
    def __init__(self):
        super().__init__()
        self.drawOrder = 0