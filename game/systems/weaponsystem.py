from engine.components.physicscomponent import PhysicsComponent
from engine.datatypes.timedevents import TimedEvent
from engine.ecs import EntitySystem, Scene, Component
from engine.scenes.levelscene import LevelScene
from game.components.projectilecomponent import ProjectileComponent
import random, time

class WeaponSystem(EntitySystem):
    def __init__(self):
        super().__init__([ProjectileComponent]) #Put target components here

        self.projectiles : list[ProjectileComponent] = []

        self.currentScene = None
    def OnEnable(self, currentScene : Scene):
        self.currentScene = currentScene
    def Update(self, currentScene: LevelScene):
        self.ProjectileUpdate(currentScene)
    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        if(isinstance(component,ProjectileComponent)):
            self.projectiles.append(component)
            component.physics = component.parentEntity.GetComponent(PhysicsComponent)

            component.physics.velocity = component.velocity

            self.StartTimedEvent(TimedEvent(self.DestroyProjectile, (self.currentScene, component.parentEntity),
                                            random.uniform(1, 2), 0,
                                            1))
    def OnDeleteComponent(self, component : Component): #Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        if(isinstance(component,ProjectileComponent)):
            self.projectiles.remove(component)

    def DestroyProjectile(self, currentScene : Scene, projectile):
        currentScene.DeleteEntity(projectile)
    def ProjectileUpdate(self, currentScene : LevelScene):
        for projectile in self.projectiles:
            overlappedTileID = currentScene.GetTileAtWorldPosition(projectile.parentEntity.position, "Walls")
            if overlappedTileID and overlappedTileID != -1:
                currentScene.DeleteEntity(projectile.parentEntity)
            projectile.parentEntity.position[0] += projectile.velocity[0] * self.game.deltaTime
            projectile.parentEntity.position[1] += projectile.velocity[1] * self.game.deltaTime