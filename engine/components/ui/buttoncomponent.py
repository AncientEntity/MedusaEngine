from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.components.rendering.textrenderer import TextRenderer
import pygame

from engine.components.ui.uicomponent import UIComponent


class ButtonComponent(UIComponent):
    def __init__(self, spriteRenderer: SpriteRenderer, textRenderer: TextRenderer):
        super().__init__()
        self.spriteRenderer : SpriteRenderer = spriteRenderer
        self.textRenderer : TextRenderer = textRenderer

        self.defaultTint: tuple = None
        self.hoveringTint: tuple = (25, 25, 25)
        self.clickingTint: tuple = (80, 80, 80)

        if(self.spriteRenderer.sprite != None):
            self.SetBoundsFromSprite()

    def SetBoundsFromSprite(self):
        self.bounds = [self.spriteRenderer.sprite.get_width(),
                       self.spriteRenderer.sprite.get_height()]