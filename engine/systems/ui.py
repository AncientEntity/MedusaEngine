import pygame.mouse

from engine.components.recttransformcomponent import RectTransformComponent
from engine.components.ui.buttoncomponent import ButtonComponent
from engine.components.ui.uicomponent import UIComponent
from engine.constants import CURSOR_NONE, CURSOR_PRESSED, CURSOR_HOVERING, ALIGN_CENTER, ALIGN_CENTERLEFT, \
    ALIGN_CENTERRIGHT, ALIGN_TOPLEFT, ALIGN_TOPRIGHT, ALIGN_BOTTOMLEFT, ALIGN_BOTTOMRIGHT, ALIGN_NONE, \
    ALIGN_CENTERBOTTOM, ALIGN_CENTERTOP
from engine.datatypes.anchor import Anchor
from engine.ecs import EntitySystem, Scene, Component
from engine.engine import Input
from engine.logging import LOG_ERRORS, Log, LOG_INFO
from engine.systems.renderer import RenderingSystem


class UISystem(EntitySystem):
    def __init__(self):
        super().__init__([UIComponent, RectTransformComponent])

        self.allUIElements = []
        self.alignComponents = []
        self.buttons = []

        self.anchors = [None,None,None,None,None,None,None,None,None]

        self._rendering : RenderingSystem = None

    def Update(self, currentScene: Scene):
        mousePosition = RenderingSystem().instance.screenMousePosition

        self.UpdateElementHoverStates(mousePosition)
        self.UpdateButtons(mousePosition)

    def UpdateElementHoverStates(self, mousePosition):
        element : UIComponent
        for element in self.allUIElements:
            element.cursorState = self.GetElementHoverState(mousePosition,element)

    def GetElementHoverState(self,mousePosition,element : UIComponent):
        if(element.screenSpace):
            screenBounds = pygame.Rect(element.parentEntity.position[0]-element.bounds[0]/2
                                       ,element.parentEntity.position[1]-element.bounds[1]/2,
                                       element.bounds[0],element.bounds[1])
        else:
            screenBounds = pygame.Rect(element.parentEntity.position[0]-element.bounds[0]/2-RenderingSystem().instance.cameraPosition[0]
                                       ,element.parentEntity.position[1]-element.bounds[1]/2-RenderingSystem().instance.cameraPosition[1],
                                       element.bounds[0],element.bounds[1])
        if(screenBounds.collidepoint(mousePosition)):
            return CURSOR_PRESSED if Input.MouseButtonPressed(0) else CURSOR_HOVERING
        return CURSOR_NONE

    def UpdateButtons(self, mousePositions):
        button : ButtonComponent
        for button in self.buttons:
            if(button.cursorState == CURSOR_NONE):
                button.spriteRenderer.sprite.SetTint(None)
            elif(button.cursorState == CURSOR_HOVERING):
                button.spriteRenderer.sprite.SetTint(button.hoveringTint)
            elif(button.cursorState == CURSOR_PRESSED):
                button.spriteRenderer.sprite.SetTint(button.clickingTint)

    def OnEnable(self, currentScene : Scene):
        self._rendering = currentScene.GetSystemByClass(RenderingSystem)
        if self._rendering:
            self._rendering.onScreenUpdated.append(self.OnResolutionUpdated)
            self.OnResolutionUpdated()
        else:
            Log("UISystem found no RenderingSystem found in scene. A RenderingSystem is required.", LOG_ERRORS)

    def OnResolutionUpdated(self):
        Log("UISystem OnResolutionUpdated", LOG_INFO)

        # Recalculate anchor positions
        self.anchors[ALIGN_CENTER] = Anchor((0,0),(0,0))
        self.anchors[ALIGN_CENTERLEFT] = Anchor((-self._rendering._scaledHalfSize[0],0), (1,0))
        self.anchors[ALIGN_CENTERRIGHT] = Anchor((self._rendering._scaledHalfSize[0],0), (-1,0))
        self.anchors[ALIGN_TOPLEFT] = Anchor((-self._rendering._scaledHalfSize[0],-self._rendering._scaledHalfSize[1]), (1,1))
        self.anchors[ALIGN_TOPRIGHT] = Anchor((self._rendering._scaledHalfSize[0],-self._rendering._scaledHalfSize[1]), (-1,1))
        self.anchors[ALIGN_BOTTOMLEFT] = Anchor((-self._rendering._scaledHalfSize[0],self._rendering._scaledHalfSize[1]), (1,-1))
        self.anchors[ALIGN_BOTTOMRIGHT] = Anchor((self._rendering._scaledHalfSize[0],self._rendering._scaledHalfSize[1]), (-1,-1))
        self.anchors[ALIGN_CENTERBOTTOM] = Anchor((0,self._rendering._scaledHalfSize[1]), (0,-1))
        self.anchors[ALIGN_CENTERTOP] = Anchor((0,-self._rendering._scaledHalfSize[1]), (0,1))

        uiElement : RectTransformComponent
        for uiElement in self.alignComponents:
            self.AlignUIComponent(uiElement)

    def AlignUIComponent(self, uiElement : RectTransformComponent):
        Log(uiElement.parentEntity.name + " here", LOG_INFO)
        if uiElement.screenSpace == False or uiElement.anchor == ALIGN_NONE:
            return
        anchorPosition = self.anchors[uiElement.anchor].position
        anchorBoundMult = self.anchors[uiElement.anchor].boundMultiplier
        uiElement.parentEntity.position = [anchorPosition[0] + uiElement.anchorOffset[0] + uiElement.bounds[0]//2*anchorBoundMult[0],
                                           anchorPosition[1] + uiElement.anchorOffset[1] + uiElement.bounds[1]//2*anchorBoundMult[1]]

    def OnNewComponent(self, component: Component):
        if (isinstance(component, ButtonComponent)):
            self.buttons.append(component)
        if (isinstance(component, RectTransformComponent)):
            self.alignComponents.append(component)
            self.AlignUIComponent(component)
        if (isinstance(component, UIComponent)):
            self.allUIElements.append(component)

    def OnDeleteComponent(self, component: Component):
        self.allUIElements.remove(component)

        if (isinstance(component, ButtonComponent)):
            componentIndex = self.buttons.index(component)
            if (componentIndex != -1):
                self.buttons.pop(componentIndex)
