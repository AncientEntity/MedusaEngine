import pygame.mouse

from engine.components.ui.buttoncomponent import ButtonComponent
from engine.components.ui.uicomponent import UIComponent
from engine.constants import CURSOR_NONE, CURSOR_PRESSED, CURSOR_HOVERING
from engine.ecs import EntitySystem, Scene, Component
from engine.engine import Input
from engine.systems.renderer import RenderingSystem


class UISystem(EntitySystem):
    def __init__(self):
        super().__init__([UIComponent])

        self.allUIElements = []
        self.buttons = []

    def Update(self, currentScene: Scene):
        mousePosition = RenderingSystem().instance.screenMousePosition

        self.UpdateElementHoverStates(mousePosition)
        self.UpdateButtons(mousePosition)

    def UpdateElementHoverStates(self, mousePosition):
        element : UIComponent
        for element in self.allUIElements:
            element.cursorState = self.GetElementHoverState(mousePosition,element)

    def GetElementHoverState(self,mousePosition,element : UIComponent):
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


    def OnNewComponent(self, component: Component):
        self.allUIElements.append(component)

        if (isinstance(component, ButtonComponent)):
            self.buttons.append(component)

    def OnDestroyComponent(self, component: Component):
        self.allUIElements.remove(component)

        if (isinstance(component, ButtonComponent)):
            componentIndex = self.buttons.index(component)
            if (componentIndex != -1):
                self.buttons.pop(componentIndex)
