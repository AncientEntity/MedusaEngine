from engine.ecs import EntitySystem, Scene, Component
from engine.tools.math import Distance
from game.components.ConsumerComponent import ConsumerComponent
from game.components.GeneratorComponent import GeneratorComponent
import time

from game.prefabs.Item import CreateItem
from game.systems.gamesystem import GameSystem
from game.systems.notificationsystem import NotificationSystem


class GeneratorSystem(EntitySystem):
    def __init__(self):
        super().__init__([GeneratorComponent]) #Put target components here
        self.blockedTime = 8
        self.blockNotify = None

    def Update(self,currentScene : Scene):
        if(not currentScene.GetSystemByClass(GameSystem).alive):
            if(self.blockNotify and self.blockNotify.IsAlive()):
                currentScene.DeleteEntity(self.blockNotify)
            return


        generator : GeneratorComponent
        for generator in currentScene.components[GeneratorComponent]:
            if(generator.lastItem != None and Distance(generator.lastItem.position,generator.parentEntity.position) < 6):
                blockedTime = time.time() - generator.lastCreatedItem
                if(blockedTime >= self.blockedTime / 2 and (self.blockNotify == None or not self.blockNotify.IsAlive())):
                    self.blockNotify = currentScene.GetSystemByClass(NotificationSystem).CreateNotification(currentScene, "Critical: Generator Backed Up!")
                if(blockedTime >= self.blockedTime):
                    currentScene.GetSystemByClass(GameSystem).SetLostScreen(currentScene, True, "Generator Jammed")
                    pass
                continue

            if(time.time() - generator.lastCreatedItem >= generator.spawnTimer):
                generator.lastCreatedItem = time.time()
                generator.lastItem = CreateItem(currentScene,generator.itemID)
                generator.lastItem.position = generator.parentEntity.position[:]



    def OnEnable(self, currentScene : Scene):
        pass
    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        pass
    def OnDeleteComponent(self, component : Component): #Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        pass