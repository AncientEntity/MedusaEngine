from engine.datatypes.timedevents import TimedEvent
import time


class Component:
    def __init__(self):
        self.parentEntity : Entity = None
        self.enabled = True # This only works if the given EntitySystem supports it.

        # Tracks whether the component has been put through OnNewComponent/OnDeleteComponent on entity systems.
        self._registered = False

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
        self.AddEntity(newEnt)
        return newEnt

    def AddEntity(self, entity):
        if(entity._alive):
            return
        self.entities.append(entity)
        for component in entity.components:
            self.AddComponent(component, entity)
        entity._alive = True

    def DeleteEntity(self,entity):
        if(not entity._alive):
            return

        #Remove components from scene components
        for component in entity.components:
            self.RemoveComponent(component)
        self.entities.remove(entity)
        entity._alive = False

    def AddComponent(self, component : Component, parentEntity):
        component.parentEntity = parentEntity
        self._newComponentQueue.append(component)
        componentType = type(component)
        if (componentType not in self.components):
            self.components[componentType] = []
        self.components[componentType].append(component)
        if component not in parentEntity.components:
            parentEntity.components.append(component)

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
        system : EntitySystem
        for system in self.systems:
            system.Update(self)
            system.TickTimedEvents()

    def Init(self):
        for system in self.systems:
            system.game = self.game
            for targetComponent in system.targetComponents:
                if (targetComponent not in self.components):
                    self.components[targetComponent] = []
            system.OnEnable(self) #Pass self into on enable (which is the scene)

    def HandleNewComponents(self): #Runs OnNewComponent for each new component (just added to the scene) for every system that it relates to.
        startComp : Component
        for startComp in self._newComponentQueue:
            for system in self.systems:
                if self.SystemUsesComponent(startComp, system):
                    # if(type(component) in system.targetComponents): #swapped out for the above line as that function considers inheritance.
                    system.OnNewComponent(startComp)
            startComp._registered = True
        self._newComponentQueue = []

    def HandleDeleteComponent(self,component : Component):
        if not component._registered:
            return
        for system in self.systems:
            if self.SystemUsesComponent(component,system):
            #if(type(component) in system.targetComponents): #swapped out for the above line as that function considers inheritance.
                system.OnDeleteComponent(component)

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

        self._alive = False
    def GetComponent(self, t):
        for component in self.components:
            if(isinstance(component,t)):
                return component
        return None
    def IsAlive(self):
        return self._alive

class EntitySystem:
    def __init__(self, targetComponents=[]):
        self.targetComponents = targetComponents
        self.game = None

        self._activeTimedEvents : list[TimedEvent] = []

    def Update(self, currentScene: Scene):
        pass

    def OnEnable(self, currentScene : Scene):
        pass

    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        pass

    def OnDeleteComponent(self, component : Component): #Called when an existing component is deleted (Use for deinitializing it from the systems involved)
        pass

    def StartTimedEvent(self, timedEvent : TimedEvent):
        self.InsertTimedEvent(timedEvent)
        #self._activeTimedEvents.append(timedEvent)
    def TickTimedEvents(self):
        timedEvent: TimedEvent
        index = 0
        currentTime = time.time()
        while index < len(self._activeTimedEvents) and self._activeTimedEvents[index].TimeUntilNextTrigger(currentTime) <= 0:
            timedEvent = self._activeTimedEvents[index]
            result = timedEvent.Tick()
            self._activeTimedEvents.remove(timedEvent)
            if result:
                self.InsertTimedEvent(timedEvent)
                index += 1

    # Inserts timed events in order of when they are supposed to be called.
    # I'm worried of the possibility of events being placed out of order if insertion takes too long and
    # timeUntil is now too old... But will test for now.
    def InsertTimedEvent(self, timedEvent : TimedEvent):
        currentTime = time.time()
        timeUntil = timedEvent.TimeUntilNextTrigger(currentTime)
        curIndex = 0

        for curIndex in range(len(self._activeTimedEvents)):
            if(self._activeTimedEvents[curIndex].TimeUntilNextTrigger(currentTime) < timeUntil):
                break

        self._activeTimedEvents.insert(curIndex, timedEvent)