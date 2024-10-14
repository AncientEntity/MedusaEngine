from engine.components.rendering.renderercomponent import RendererComponent
from engine.constants import ALIGN_CENTER, ALIGN_CENTERRIGHT, ALIGN_BOTTOMLEFT, ALIGN_BOTTOMRIGHT, ALIGN_CENTERLEFT, \
    ALIGN_TOPRIGHT, ALIGN_CENTERTOP
from engine.datatypes.sprites import Sprite
import pygame
class TextRenderer(RendererComponent):
    def __init__(self, text : str, font : pygame.Font):
        super().__init__()
        self._text = None
        self._render = None
        self._color = (0,0,0)
        self._antialiased = True

        self._shadowEnabled = False
        self._shadowColor = (0,0,0)
        self._shadowOffset = 2

        self._textAlign = ALIGN_CENTER
        self._alignOffset = (0,0)

        self.SetText(text)

        self.drawOrder = 100
        self.screenSpace = True #If false it will be rendered onto world space. Setting it to True will essentially be UI
    def Render(self):

        #If no shadow
        if(not self._shadowEnabled):
            self._render = Sprite(self._font.render(self._text,self._antialiased,self._color))
        else:
            frontRender = self._font.render(self._text,self._antialiased,self._color)
            backRender = self._font.render(self._text,self._antialiased,self._shadowColor)
            textSurface = pygame.Surface((frontRender.get_width()+1,frontRender.get_height()+1), pygame.SRCALPHA, 32)
            textSurface.blit(backRender,[2,2])
            textSurface.blit(frontRender,[0,0])
            self._render = Sprite(textSurface)

        self.CalculateAlignmentOffset()
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
    def SetAlign(self, alignment): # See ALIGN_* Constants in engine/constants.py
        if(self._textAlign == alignment):
            return
        self._textAlign = alignment
        self.CalculateAlignmentOffset()
    def SetShadow(self, hasShadow : bool, shadowColor, offset : int):
        if(self._shadowEnabled == hasShadow and self._shadowColor == shadowColor):
            return
        self._shadowEnabled = hasShadow
        self._shadowColor = shadowColor
        self._shadowOffset = offset
        self.Render()


    def CalculateAlignmentOffset(self):
        xOffset = 0
        yOffset = 0

        if (self._textAlign == ALIGN_CENTER):
            xOffset = self._render.get_width() // 2
            yOffset = self._render.get_height() // 2
        else:
            if(self._textAlign == ALIGN_CENTERRIGHT or self._textAlign == ALIGN_TOPRIGHT or self._textAlign == ALIGN_BOTTOMRIGHT):
                xOffset = self._render.get_width()
            if(self._textAlign == ALIGN_CENTERRIGHT or self._textAlign == ALIGN_CENTERLEFT):
                yOffset = self._render.get_height() // 2
            if(self._textAlign == ALIGN_CENTERTOP):
                xOffset = self._render.get_width() // 2
            if(self._textAlign == ALIGN_BOTTOMLEFT or self._textAlign == ALIGN_BOTTOMRIGHT):
                yOffset = self._render.get_height()


        # We don't need to do anything for ALIGN_TOPLEFT as RenderingSystem without offset takes the top left.

        self._alignOffset = (xOffset,yOffset) # Tuple for memory efficiency and speed :)

    def SetAntialiased(self,antialias : bool):
        if(self._antialiased == antialias):
            return
        self._antialiased = antialias
        self.Render()