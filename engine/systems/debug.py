import pygame

from engine.components.debug.debugcomponent import DebugComponent
from engine.datatypes.font import Font
from engine.ecs import EntitySystem, Scene, Component


class DebugSystem(EntitySystem):
    def __init__(self):
        super().__init__([DebugComponent])
        self.removeOnHeadless = True

        self.active = True

        self.debugs : list[DebugComponent] = []

        self.font = Font("Arial")
        self.fontInstance = self.font.GetPygameFont(12,False,False)

    def Update(self,currentScene : Scene):
        if not self.active:
            return
        dumps = []
        for debugComponent in self.debugs:
            if debugComponent.collector:
                dumps.append(debugComponent.collector.__class__.__name__)
                for dump in debugComponent.collector.Collect(self.game, debugComponent.parentEntity, currentScene):
                    dumps.append(dump)

        curY = 0
        for dump in dumps:
            textSurface = self.fontInstance.render(dump,True,(0,0,0))

            self.game.display.blit(textSurface,(0,curY))

            curY += textSurface.get_height() + 2


    def OnDisable(self, currentScene : Scene):
        pass

    def OnNewComponent(self,component : Component):
        if isinstance(component, DebugComponent):
            self.debugs.append(component)

    def OnDeleteComponent(self, component : Component):
        if isinstance(component, DebugComponent) and component in self.debugs:
            self.debugs.remove(component)