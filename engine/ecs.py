from engine.logging import *

class Scene:
    def __init__(self):
        self.systems: list[EntitySystem] = []
        self.entities = []
        self.components = {}
        self.game = None

    def AddComponent(self, component):
        componentType = type(component)
        if (componentType not in self.components):
            self.components[componentType] = []
        self.components[componentType].append(component)

    def RemoveComponent(self, component):
        componentType = type(component)
        if (componentType in self.components):
            self.components[componentType].remove(component)

    def GetSystemByClass(self,systemType : type):
        for system in self.systems:
            if(type(system) == systemType):
                return system
        return None

    def Update(self):
        for system in self.systems:
            system.Update(self)

    def Init(self):
        for system in self.systems:
            system.game = self.game
            for targetComponent in system.targetComponents:
                if (targetComponent not in self.components):
                    self.components[targetComponent] = []
            system.OnEnable()


class Component:
    def __init__(self, parentEntity):
        self.parentEntity = parentEntity


class Entity:
    def __init__(self):
        self.name = "Unnamed Entity"
        self.position = (0, 0)
        self.components = []


class EntitySystem:
    def __init__(self, targetComponents=[]):
        self.targetComponents = targetComponents
        self.game = None

    def Update(self, currentScene: Scene):
        pass

    def OnEnable(self):
        pass
