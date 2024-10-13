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
        self.rectTransforms = []
        self.buttons = []

        self.rootRect = None

        self._rendering: RenderingSystem = None

    def Update(self, currentScene: Scene):
        mousePosition = RenderingSystem().instance.screenMousePosition

        self.UpdateElementHoverStates(mousePosition)
        self.UpdateButtons(mousePosition)

    def UpdateElementHoverStates(self, mousePosition):
        element: UIComponent
        for element in self.allUIElements:
            element.cursorState = self.GetElementHoverState(mousePosition, element)

    def GetElementHoverState(self, mousePosition, element: UIComponent):
        if (element.screenSpace):
            screenBounds = pygame.Rect(element.parentEntity.position[0] - element.bounds[0] / 2
                                       , element.parentEntity.position[1] - element.bounds[1] / 2,
                                       element.bounds[0], element.bounds[1])
        else:
            screenBounds = pygame.Rect(
                element.parentEntity.position[0] - element.bounds[0] / 2 - RenderingSystem().instance.cameraPosition[0]
                ,
                element.parentEntity.position[1] - element.bounds[1] / 2 - RenderingSystem().instance.cameraPosition[1],
                element.bounds[0], element.bounds[1])
        if (screenBounds.collidepoint(mousePosition)):
            return CURSOR_PRESSED if Input.MouseButtonPressed(0) else CURSOR_HOVERING
        return CURSOR_NONE

    def UpdateButtons(self, mousePositions):
        button: ButtonComponent
        for button in self.buttons:
            if (button.cursorState == CURSOR_NONE):
                button.spriteRenderer.sprite.SetTint(None)
            elif (button.cursorState == CURSOR_HOVERING):
                button.spriteRenderer.sprite.SetTint(button.hoveringTint)
            elif (button.cursorState == CURSOR_PRESSED):
                button.spriteRenderer.sprite.SetTint(button.clickingTint)

    def OnEnable(self, currentScene: Scene):
        self._rendering = currentScene.GetSystemByClass(RenderingSystem)
        if self._rendering:
            self._rendering.onScreenUpdated.append(self.OnResolutionUpdated)
            self.OnResolutionUpdated()
        else:
            Log("UISystem found no RenderingSystem found in scene. A RenderingSystem is required.", LOG_ERRORS)

    def OnResolutionUpdated(self):
        Log(f"UISystem OnResolutionUpdated, New Size: {self._rendering._scaledScreenSize}", LOG_INFO)
        if not self.rootRect:
            self.rootRect = RectTransformComponent(ALIGN_CENTER, (0, 0), self._rendering._scaledScreenSize)
        else:
            self.rootRect.bounds = self._rendering._scaledScreenSize

        self.rootRect.CalculateAnchors((0, 0), self._rendering._scaledHalfSize)
        self.UpdateRectTransform(self.rootRect)

    def UpdateRectTransform(self, transform: RectTransformComponent):
        if transform != self.rootRect:
            targetAnchor: Anchor = transform._parentRect._anchors[transform._anchor]
            newPosition = [targetAnchor.position[0] + transform._anchorOffset[0],
                           targetAnchor.position[1] + transform._anchorOffset[1]]
            newPosition[0] += transform.bounds[0] // 2 * targetAnchor.boundMultiplier[0]
            newPosition[1] += transform.bounds[1] // 2 * targetAnchor.boundMultiplier[1]

            transform.parentEntity.position = newPosition
            transform.CalculateAnchors(newPosition,
                                       (transform.bounds[0] // 2, transform.bounds[1] // 2))

        for child in transform._children:
            self.UpdateRectTransform(child)

    def DebugDrawRects(self):
        rect: RectTransformComponent
        for rect in self.rectTransforms:
            pygame.draw.rect(self._rendering._renderTarget, (50, 255, 50), (
            rect._anchors[ALIGN_CENTER].position[0] + self._rendering._scaledHalfSize[0] - rect.bounds[0] // 2,
            rect._anchors[ALIGN_CENTER].position[1] + self._rendering._scaledHalfSize[1] - rect.bounds[1] // 2,
            rect.bounds[0],
            rect.bounds[1]), 1)
            i = 0
            for anchor in rect._anchors:
                pygame.draw.circle(self._rendering._renderTarget, (255 - (i + 1) / 9 * 255, 0, (i + 1) / 9 * 255),
                                   (anchor.position[0] + self._rendering._scaledHalfSize[0]
                                    , anchor.position[1] + self._rendering._scaledHalfSize[1]), 2)
                i += 1

    def SetParent(self, rect: RectTransformComponent, newParent: RectTransformComponent):
        rect.InternalSetParent(newParent)
        self.UpdateRectTransform(rect)

    def OnNewComponent(self, component: Component):
        if (isinstance(component, ButtonComponent)):
            self.buttons.append(component)
        if (isinstance(component, RectTransformComponent)):
            self.rectTransforms.append(component)
            if component._parentRect == None:
                component.InternalSetParent(self.rootRect)

            self.UpdateRectTransform(component)
        if (isinstance(component, UIComponent)):
            self.allUIElements.append(component)

    def OnDeleteComponent(self, component: Component):
        self.allUIElements.remove(component)

        if (isinstance(component, ButtonComponent)):
            componentIndex = self.buttons.index(component)
            if (componentIndex != -1):
                self.buttons.pop(componentIndex)
