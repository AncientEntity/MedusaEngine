from engine.components.rendering.renderercomponent import RendererComponent
from engine.datatypes.sprites import Sprite
from pygame import Surface


class SpriteRenderer(RendererComponent):
    def __init__(self, sprite : Sprite or Surface, drawOrder=0):
        super().__init__()
        self.drawOrder = drawOrder
        self.sprite : Sprite
        if(isinstance(sprite,Surface)):
            self.sprite = Sprite(sprite)
        else:
            self.sprite = sprite