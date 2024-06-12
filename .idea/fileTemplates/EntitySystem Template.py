from engine.ecs import EntitySystem, Scene


class TemplateSystem(EntitySystem):
    def __init__(self):
        super().__init__([]) #Put target components here

    def Update(self,currentScene : Scene):
        pass
    def OnEnable(self, currentScene : Scene):
        pass
    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        pass
    def OnDestroyComponent(self, component : Component): #Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        pass