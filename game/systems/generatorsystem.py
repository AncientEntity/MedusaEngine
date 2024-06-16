from engine.ecs import EntitySystem, Scene, Component
from engine.tools.math import Distance
from game.components.ConsumerComponent import ConsumerComponent
from game.components.GeneratorComponent import GeneratorComponent
import time

from game.prefabs.Item import CreateItem


class GeneratorSystem(EntitySystem):
    def __init__(self):
        super().__init__([GeneratorComponent]) #Put target components here

    def Update(self,currentScene : Scene):
        generator : GeneratorComponent
        for generator in currentScene.components[GeneratorComponent]:
            if(generator.lastItem != None and Distance(generator.lastItem.position,generator.parentEntity.position) < 10):
                generator.lastCreatedItem = time.time()
                continue

            if(time.time() - generator.lastCreatedItem >= generator.spawnTimer):
                generator.lastCreatedItem = time.time()
                generator.lastItem = CreateItem(currentScene,generator.itemID)
                generator.lastItem.position = generator.parentEntity.position[:]



    def OnEnable(self, currentScene : Scene):
        pass
    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        pass
    def OnDestroyComponent(self, component : Component): #Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        pass