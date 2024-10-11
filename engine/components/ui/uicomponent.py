from engine.components.recttransformcomponent import RectTransformComponent
from engine.constants import CURSOR_NONE, ALIGN_NONE, ALIGN_CENTER
from engine.ecs import Component

class UIComponent(RectTransformComponent):
    def __init__(self):
        super().__init__()
        self.cursorState = CURSOR_NONE