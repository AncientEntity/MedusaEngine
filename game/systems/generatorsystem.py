from engine.ecs import EntitySystem, Scene, Component
from game.components.GeneratorComponent import GeneratorComponent
import time

from game.prefabs.Item import CreateItem


class GeneratorSystem(EntitySystem):
    def __init__(self):
        super().__init__([GeneratorComponent]) #Put target components here

    def Update(self,currentScene : Scene):
        generator : GeneratorComponent
        for generator in currentScene.components[GeneratorComponent]:
            if(time.time() - generator.lastCreatedItem >= generator.spawnTimer):
                generator.lastCreatedItem = time.time()
                newItem = CreateItem(currentScene,generator.itemID)
                newItem.position = generator.parentEntity.position[:]
                print("Spawn Item:",newItem.position)


    def OnEnable(self, currentScene : Scene):
        pass
    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        pass
    def OnDestroyComponent(self, component : Component): #Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        pass