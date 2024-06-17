from engine.constants import CURSOR_NONE
from engine.ecs import Component

class UIComponent(Component):
    def __init__(self):
        super().__init__()
        self.bounds = [0,0]
        self.cursorState = CURSOR_NONE