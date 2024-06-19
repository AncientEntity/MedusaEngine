from engine.components.rendering.renderercomponent import RendererComponent
from engine.datatypes.sprites import Sprite
import pygame

class TextRenderer(RendererComponent):
    def __init__(self, text : str, font : pygame.Font):
        super().__init__()
        self._text = None
        self._font = font
        self._render = None
        self._color = (0,0,0)
        self._antialiased = True
        self.SetText(text)

        self.drawOrder = 100
        self.screenSpace = True #If false it will be rendered onto world space. Setting it to True will essentially be UI
    def Render(self):
        self._render = Sprite(self._font.render(self._text,self._antialiased,self._color))
    def SetText(self,text):
        if(text == self._text):
            return
        self._text = text
        self.Render()
    def SetFont(self,font : pygame.Font):
        if(font == self._font):
            return
        self._font = font
        self.Render()
    def SetColor(self,color):
        if(color == self._color):
            return
        self._color = color
        self.Render()
    def SetAlpha(self,alpha):
        if(self._render._alpha == alpha):
            return
        self.Render()
        self._render.SetAlpha(alpha)
    def SetAntialiased(self,antialias : bool):
        if(self._antialiased == antialias):
            return
        self._antialiased = antialias
        self.Render()

