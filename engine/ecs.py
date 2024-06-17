
class Component:
    def __init__(self):
        self.parentEntity : Entity = None


class Scene:
    def __init__(self):
        self.name = "Unnamed Scene"
        self.systems: list[EntitySystem] = []
        self.entities = []
        self.components = {}
        self.game = None

        self._newComponentQueue = [] #Contains the list of components just added into the scene. For running EntitySystem.OnNewComponent on them.

    def CreateEntity(self,name,position,components):
        newEnt = Entity()
        newEnt.name = name
        newEnt.position = position
        newEnt.components = components
        self.entities.append(newEnt)
        for component in newEnt.components:
            self.AddComponent(component, newEnt)
        return newEnt

    def DeleteEntity(self,entity):
        #Remove components from scene components
        for component in entity.components:
            self.RemoveComponent(component)
        self.entities.remove(entity)

    def AddComponent(self, component : Component, parentEntity):
        component.parentEntity = parentEntity
        self._newComponentQueue.append(component)
        componentType = type(component)
        if (componentType not in self.components):
            self.components[componentType] = []
        self.components[componentType].append(component)

    def RemoveComponent(self, component : Component):
        componentType = type(component)
        if (componentType in self.components):
            self.HandleDeleteComponent(component)
            self.components[componentType].remove(component)

    def GetSystemByClass(self,systemType : type):
        for system in self.systems:
            if(type(system) == systemType):
                return system
        return None

    def Update(self):
        #Run OnNewComponent for each component in its related systems.
        self.HandleNewComponents()

        #Run each system's update.
        for system in self.systems:
            system.Update(self)

    def Init(self):
        for system in self.systems:
            system.game = self.game
            for targetComponent in system.targetComponents:
                if (targetComponent not in self.components):
                    self.components[targetComponent] = []
            system.OnEnable(self) #Pass self into on enable (which is the scene)

    def HandleNewComponents(self): #Runs OnNewComponent for each new component (just added to the scene) for every system that it relates to.
        for startComp in self._newComponentQueue:
            for system in self.systems:
                if self.SystemUsesComponent(startComp, system):
                    # if(type(component) in system.targetComponents): #swapped out for the above line as that function considers inheritance.
                    system.OnNewComponent(startComp)
        self._newComponentQueue = []

    def HandleDeleteComponent(self,component : Component):
        for system in self.systems:
            if self.SystemUsesComponent(component,system):
            #if(type(component) in system.targetComponents): #swapped out for the above line as that function considers inheritance.
                system.OnDestroyComponent(component)

    def SystemUsesComponent(self, component : Component, system):
        for componentType in system.targetComponents:
            if isinstance(component,componentType):
                return True
        return False

    def Clear(self):
        self.components = {}
        self.entities = []


class Entity:
    def __init__(self):
        self.name = "Unnamed Entity"
        self.position = (0, 0)
        self.components = []
    def GetComponent(self, t):
        for component in self.components:
            if(isinstance(component,t)):
                return component
        return None

class EntitySystem:
    def __init__(self, targetComponents=[]):
        self.targetComponents = targetComponents
        self.game = None

    def Update(self, currentScene: Scene):
        pass

    def OnEnable(self, currentScene : Scene):
        pass

    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        pass

    def OnDestroyComponent(self, component : Component): #Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        pass