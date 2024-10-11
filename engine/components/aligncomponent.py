from engine.constants import CURSOR_NONE, ALIGN_NONE, ALIGN_CENTER
from engine.ecs import Component

class AlignComponent(Component):
    def __init__(self, anchor=ALIGN_CENTER, anchorOffset=(0,0), screenSpace=True):
        super().__init__()

        # anchor and anchorOffset only apply when screenSpace = True
        self.screenSpace = screenSpace
        self.anchor = anchor
        self.anchorOffset = anchorOffset