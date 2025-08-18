from engine.components.rendering.renderercomponent import RendererComponent
from engine.datatypes.sprites import Sprite
from pygame import Surface


class SpriteRenderer(RendererComponent):
    def __init__(self, sprite : Sprite or Surface, drawOrder=0, screenSpace=False):
        super().__init__()
        self.drawOrder = drawOrder
        self.sprite : Sprite = None
        self.screenSpace = screenSpace

        self.offset = [0,0]

        # If this component has a sibling RectTransformComponent and self.rectMargin is set to a tuple such as (0.5,0.5)
        # It will gain that margin within the rect.
        self.rectMargin = None

        self.SetSprite(sprite)

    def SetSprite(self, newSprite : Sprite or Surface):
        if(isinstance(newSprite,Surface)):
            self.sprite = Sprite(newSprite)
        else:
            self.sprite = newSprite