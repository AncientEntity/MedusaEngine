from engine.constants import CURSOR_NONE, ALIGN_NONE, ALIGN_CENTER, ALIGN_CENTERLEFT, ALIGN_CENTERRIGHT, ALIGN_TOPLEFT, \
    ALIGN_TOPRIGHT, ALIGN_BOTTOMLEFT, ALIGN_BOTTOMRIGHT, ALIGN_CENTERBOTTOM, ALIGN_CENTERTOP
from engine.datatypes.anchor import Anchor
from engine.ecs import Component

class RectTransformComponent(Component):
    def __init__(self, anchor=ALIGN_CENTER, anchorOffset=(0,0), bounds=(16,16), parent=None, screenSpace=True):
        super().__init__()
        self.bounds = bounds

        # anchor and anchorOffset only apply when screenSpace = True
        self.screenSpace = screenSpace
        self.anchor = anchor
        self.anchorOffset = anchorOffset
        self.parentRect = parent

        self._children = []
        self._anchors = [None, None, None, None, None, None, None, None, None]

        if self.parentRect:
            self.parentRect._children.append(self)

    def CalculateAnchors(self, newCenter, parentHalfSize):
        self._anchors[ALIGN_CENTER] = Anchor((newCenter[0], newCenter[1]), (0, 0))
        self._anchors[ALIGN_CENTERLEFT] = Anchor((-parentHalfSize[0] + newCenter[0], newCenter[1]), (1, 0))
        self._anchors[ALIGN_CENTERRIGHT] = Anchor((parentHalfSize[0] + newCenter[0], newCenter[1]), (-1, 0))
        self._anchors[ALIGN_TOPLEFT] = Anchor((-parentHalfSize[0] + newCenter[0], -parentHalfSize[1] + newCenter[1]), (1, 1))
        self._anchors[ALIGN_TOPRIGHT] = Anchor((parentHalfSize[0] + newCenter[0], -parentHalfSize[1] + newCenter[1]), (-1, 1))
        self._anchors[ALIGN_BOTTOMLEFT] = Anchor((-parentHalfSize[0] + newCenter[0], parentHalfSize[1] + newCenter[1]), (1, -1))
        self._anchors[ALIGN_BOTTOMRIGHT] = Anchor((parentHalfSize[0] + newCenter[0], parentHalfSize[1] + newCenter[1]), (-1, -1))
        self._anchors[ALIGN_CENTERBOTTOM] = Anchor((newCenter[0], parentHalfSize[1] + newCenter[1]), (0, -1))
        self._anchors[ALIGN_CENTERTOP] = Anchor((newCenter[0], -parentHalfSize[1] + newCenter[1]), (0, 1))