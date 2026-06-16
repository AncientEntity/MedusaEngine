from engine.constants import NET_HOST
from engine.datatypes.timedevents import TimedEvent
import time
import random

from engine.networking.networkstate import NetworkState
from engine.networking.stateassert import StateAssert
from engine.networking.variables.networkvarbase import NetworkVarBase
from engine.networking.variables.networkvarbool import NetworkVarBool
from engine.networking.variables.networkvarvector import NetworkVarVector
from engine.networking.variables.networkvarvectori import NetworkVarVectorInterpolate
from engine.tools.platform import IsHeadless


class Component:
    def __init__(self):
        self.parentEntity : Entity = None
        self._enabled = True # This only works if the given EntitySystem supports it.

        # Tracks whether the component has been put through OnNewComponent/OnDeleteComponent on entity systems.
        self._registered = False
    def get_enabled(self):
        if isinstance(self._enabled, NetworkVarBool):
            return self._enabled.Get()
        else:
            return self._enabled
    def set_enabled(self, newValue):
        if isinstance(self._enabled, NetworkVarBool):
            self._enabled.Set(newValue)
        else:
            self._enabled = newValue

    enabled = property(get_enabled, set_enabled)

    # This should be ran when making the component, not midway through it's existence. Must be ran for everyone.
    def setup_enabled_networking(self):
        self._enabled = NetworkVarBool(self._enabled)

class Scene:
    def __init__(self):
        self.name = "Unnamed Scene"
        self.systems: list[EntitySystem] = []
        self.entities = []
        self.components = {}
        self.game = None
        self.sceneSize = (2**21,2**21) # Note: the maximum size pygame.Rect seems to support is (x=-2**29,y=2**29,
                                       #                                                         w=2**30, 2**30)
                                       # Should be a power of 2.

        self._newComponentQueue = [] #Contains the list of components just added into the scene. For running EntitySystem.OnNewComponent on them.

        self.networkedEntities = {} # List of just the network entities (they are also in self.entities)
        self.networkDeletedQueue = []

    def CreateEntity(self,name,position,components):
        newEnt = Entity()
        newEnt.name = name
        newEnt.position = position
        newEnt.components = components
        self.AddEntity(newEnt)
        return newEnt

    def CreateNetworkEntity(self, name, position, components, ownerId, netentityId=None):
        newEnt = NetworkEntity(ownerId, netentityId)
        newEnt.name = name
        newEnt.engine_get_position_network_variable().Set(position)
        newEnt.components = components
        self.AddEntity(newEnt)
        return newEnt

    def AddEntity(self, entity):
        if(entity._alive):
            return
        self.entities.append(entity)
        if isinstance(entity, NetworkEntity):
            self.networkedEntities[entity.entityId] = entity
        for component in entity.components:
            self.AddComponent(component, entity)
        entity._alive = True

    def DeleteEntity(self,entity, appendDeletionQueue=True):
        if(not entity._alive):
            return

        #Remove components from scene components
        for component in entity.components:
            self.RemoveComponent(component)
        self.entities.remove(entity)
        if isinstance(entity, NetworkEntity):
            self.networkedEntities.pop(entity.entityId)
            if appendDeletionQueue:
                self.networkDeletedQueue.append(entity)
        entity._alive = False

    def AddComponent(self, component : Component, parentEntity):
        component.parentEntity = parentEntity
        self._newComponentQueue.append(component)
        if component not in parentEntity.components:
            parentEntity.components.append(component)

    def RemoveComponent(self, component : Component):
        componentType = type(component)
        if (componentType in self.components):
            self.HandleDeleteComponent(component)

            while componentType != object:
                self.components[componentType].remove(component)
                componentType = componentType.__bases__[0]

    def AddComponents(self, components : list[Component], parentEntity):
        for component in components:
            self.AddComponent(component, parentEntity)

    def GetSystemByClass(self,systemType : type):
        for system in self.systems:
            if(type(system) == systemType):
                return system
        return None
    def GetSystemByName(self, systemName : str):
        for system in self.systems:
            if(systemName in str(type(system))):
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
        for system in self.systems[:]:
            if system.removeOnHeadless and IsHeadless():
                self.systems.remove(system)
                continue

            system.game = self.game
            for targetComponent in system.targetComponents:
                if (targetComponent not in self.components):
                    self.components[targetComponent] = []
            system.OnEnable(self) #Pass self into on enable (which is the scene)

    def Disable(self):
        for system in self.systems:
            system.OnDisable(self)

    def HandleNewComponents(self): #Runs OnNewComponent for each new component (just added to the scene) for every system that it relates to.
        startComp : Component
        for startComp in self._newComponentQueue:
            # Add component to self.components dictionary lists.
            componentType = type(startComp)
            while componentType != object:
                if (componentType not in self.components):
                    self.components[componentType] = []
                self.components[componentType].append(startComp)
                componentType = componentType.__bases__[0]

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
        component._registered = False

    def SystemUsesComponent(self, component : Component, system):
        for componentType in system.targetComponents:
            if isinstance(component,componentType):
                return True
        return False

    def Clear(self):
        self.components = {}
        self.entities = []

class Entity:
    takenIds = set()
    def __init__(self, forcedId=None):
        if not forcedId:
            self.entityId = Entity.GenerateEntityId()
        else:
            self.entityId = forcedId

        Entity.takenIds.add(self.entityId)

        self.name = "Unnamed Entity"
        self.position = (0, 0)
        self.components = []
        self.ownerId = None # Used for multiplayer (see NetworkEntity)

        self.prefabName = None

        self._alive = False

    def GetComponent(self, t):
        for component in self.components:
            if(isinstance(component,t)):
                return component
        return None
    def GetComponents(self, t):
        found = []
        for component in self.components:
            if(isinstance(component,t)):
                found.append(component)
        return found

    def IsAlive(self):
        return self._alive

    @staticmethod
    def GenerateEntityId():
        found = False
        while not found:
            potentialId = random.randint(0,2**30)
            if potentialId not in Entity.takenIds:
                found = True
        return potentialId

    def get_exact_position(self):
        return self.position


class NetworkEntity(Entity):
    def __init__(self, ownerId, forcedId=None):
        self._position = NetworkVarVectorInterpolate()
        self._position.serverAuthorityRequired = True

        # Entity ID for networked object is always negative.
        if forcedId is not None:
            super().__init__(-abs(forcedId))
        else:
            super().__init__()
            self.entityId = -abs(self.entityId)

        self._networkVariables = None
        self._networkVariablesDict = None

        self.ownerId = ownerId

    def GetNetworkVariables(self):
        if self._networkVariables:
            return self._networkVariables
        hasAuthority = NetworkState.clientId == self.ownerId or NetworkState.identity & NET_HOST

        self._networkVariablesDict = {}
        self._networkVariables = []
        self._networkVariables.append(("_position", self._position))
        self._networkVariablesDict["_position"] = self._position
        if hasAuthority:
            self._position.hasAuthority = hasAuthority and (not self._position.serverAuthorityRequired or NetworkState.identity & NET_HOST)
        for component in self.components:
            for attr in dir(component):
                attrValue = getattr(component, attr)
                if isinstance(attrValue, NetworkVarBase):
                    self._networkVariables.append((attr, attrValue))
                    self._networkVariablesDict[attr] = attrValue
                    attrValue.hasAuthority = hasAuthority and (not attrValue.serverAuthorityRequired or NetworkState.identity & NET_HOST)
        return self._networkVariables

    def get_network_variables_dict(self):
        if not self._networkVariablesDict:
            self.GetNetworkVariables()
        return self._networkVariablesDict
    def engine_get_position_network_variable(self):
        return self._position
    def get_position(self):
        return self._position.Get()
    def set_position(self, value):
        self._position.Set(value, self._position.hasAuthority)

    def get_exact_position(self):
        return self._position.GetExact()

    position = property(get_position,
                                 set_position)


class EntitySystem:
    def __init__(self, targetComponents=[]):
        self.targetComponents = targetComponents
        self.game = None

        self.removeOnHeadless = False

        self._activeTimedEvents : list[TimedEvent] = []

    def Update(self, currentScene: Scene):
        pass

    def OnEnable(self, currentScene : Scene):
        pass
    def OnDisable(self, currentScene : Scene):
        pass

    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        pass

    def OnDeleteComponent(self, component : Component): #Called when an existing component is deleted (Use for deinitializing it from the systems involved)
        pass

    def StartTimedEvent(self, timedEvent : TimedEvent):
        self.InsertTimedEvent(timedEvent)
    def CancelTimedEvent(self, timedEvent : TimedEvent):
        for index in range(len(self._activeTimedEvents)):
            if(self._activeTimedEvents[index] == timedEvent):
                self._activeTimedEvents.pop(index)
                return True
        return False

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
            if timeUntil <= self._activeTimedEvents[curIndex].TimeUntilNextTrigger(currentTime):
                break

        self._activeTimedEvents.insert(curIndex, timedEvent)