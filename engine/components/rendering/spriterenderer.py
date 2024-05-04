from engine.components.rendering.renderercomponent import RendererComponent
from engine.datatypes.sprites import Sprite
from pygame import Surface


class SpriteRenderer(RendererComponent):
    def __init__(self, sprite : Sprite or Surface):
        super().__init__()
        self.sprite = sprite