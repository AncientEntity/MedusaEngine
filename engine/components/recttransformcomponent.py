from engine.constants import CURSOR_NONE, ALIGN_NONE, ALIGN_CENTER
from engine.ecs import Component

class RectTransformComponent(Component):
    def __init__(self, anchor=ALIGN_CENTER, anchorOffset=(0,0),bounds=(16,16), screenSpace=True):
        super().__init__()
        self.bounds = bounds

        # anchor and anchorOffset only apply when screenSpace = True
        self.screenSpace = screenSpace
        self.anchor = anchor
        self.anchorOffset = anchorOffset