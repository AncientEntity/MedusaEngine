from engine.components.aligncomponent import AlignComponent
from engine.constants import CURSOR_NONE, ALIGN_NONE, ALIGN_CENTER
from engine.ecs import Component

class UIComponent(AlignComponent):
    def __init__(self):
        super().__init__()
        self.bounds = [0,0]
        self.cursorState = CURSOR_NONE