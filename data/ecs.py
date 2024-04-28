from data.logging import *


class Scene:
    def __init__(self):
        self.systems : list[EntitySystem] = []
        self.entities = []
        self.components = {}
    def AddComponent(self,component):
        componentType = type(component)
        if(componentType not in self.components):
            self.components[componentType] = []
        self.components[componentType].append(component)
    def RemoveComponent(self,component):
        componentType = type(component)
        if(componentType in self.components):
            self.components[componentType].remove(component)
    def Update(self):
        for system in self.systems:
            system.Update(self)
    def Init(self):
        for system in self.systems:
            for targetComponent in system.targetComponents:
                if(targetComponent not in self.components):
                    self.components[targetComponent] = []

class Component:
    def __init__(self,parentEntity):
        self.parentEntity = parentEntity

class Entity:
    def __init__(self):
        self.name = "Unnamed Entity"
        self.position = (0,0)
        self.components = []

class EntitySystem:
    def __init__(self,targetComponents=[]):
        self.targetComponents = targetComponents
    def Update(self,currentScene : Scene):
        pass