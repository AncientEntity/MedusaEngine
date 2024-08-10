from engine.components.physicscomponent import PhysicsComponent
from engine.datatypes.timedevents import TimedEvent
from engine.ecs import EntitySystem, Scene, Component
from game.components.projectilecomponent import ProjectileComponent
import random, time

class WeaponSystem(EntitySystem):
    def __init__(self):
        super().__init__([ProjectileComponent]) #Put target components here

        self.projectiles : list[ProjectileComponent] = []

        self.currentScene = None
    def OnEnable(self, currentScene : Scene):
        self.currentScene = currentScene
    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        if(isinstance(component,ProjectileComponent)):
            self.projectiles.append(component)
            component.physics = component.parentEntity.GetComponent(PhysicsComponent)

            component.physics.velocity = component.velocity

            self.StartTimedEvent(TimedEvent(self.DestroyProjectile, (self.currentScene, component.parentEntity),
                                            random.uniform(3, 5), 0,
                                            1))
    def OnDeleteComponent(self, component : Component): #Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        if(isinstance(component,ProjectileComponent)):
            self.projectiles.remove(component)

    def DestroyProjectile(self, currentScene : Scene, projectile):
        currentScene.DeleteEntity(projectile)