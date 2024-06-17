from engine.ecs import Component

class RendererComponent(Component):
    def __init__(self):
        super().__init__()
        self.drawOrder = 0

        #todo implement screen space rendering!
        self.screenSpace = False #If false it will be rendered onto world space. Setting it to True will essentially be UI