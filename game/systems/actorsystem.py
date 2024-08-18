from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.ecs import EntitySystem, Scene, Component, Entity
from engine.engine import Input
from engine.systems.renderer import RenderingSystem
from engine.tools.math import MoveTowards, Distance, LookAt
from game.components.actorcomponent import ActorComponent
from game.components.guncomponent import GunComponent
import time

from game.drivers.playerdriver import PlayerDriver
from game.drivers.testaidriver import TestAIDriver


class ActorSystem(EntitySystem):
    def __init__(self):
        super().__init__([ActorComponent]) #Put target components here

        self.actors : list[ActorComponent] = []
        self.actions = {}

        # Register default actions
        self.RegisterAction("up", self.ActionMoveUp)
        self.RegisterAction("down", self.ActionMoveDown)
        self.RegisterAction("left", self.ActionMoveLeft)
        self.RegisterAction("right", self.ActionMoveRight)
        self.RegisterAction("attack1", self.ActionAttack1)

        # Rendering/Camera
        self.renderingSystem : RenderingSystem = None
        self.cameraTarget : Entity = None
        self.cameraPosition = None # Contains the same list that the rendering system has.
        self.cameraSpeed = 500

    def Update(self,currentScene : Scene):
        actor : ActorComponent
        for actor in self.actors:
            if not actor.driver:
                continue

            # Reset movement this tick
            actor._movementThisTick = [0,0]

            # Trigger update
            actor.driver.Update(actor, currentScene)

            # Handle action update
            for actionName, actionFunc in actor.driver.inputs.items():
                if actionFunc and actionFunc():
                    # do action
                    self.actions[actionName](actor, currentScene)

            self.ActorMovementTick(actor)
            self.ActorItemTick(actor)

        if self.cameraTarget:
            self.CameraTick()

        import pygame, random
        if Input.KeyDown(pygame.K_t):
            randEnt = self.actors[random.randint(0,len(self.actors)-1)]
            self.cameraTarget.GetComponent(ActorComponent).driver = TestAIDriver()
            self.cameraTarget = randEnt.parentEntity
            randEnt.driver = PlayerDriver()

    def OnEnable(self, currentScene : Scene):
        # Grab rendering system and camera position
        self.renderingSystem = currentScene.GetSystemByClass(RenderingSystem)
        self.cameraPosition = self.renderingSystem.cameraPosition


    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        if(isinstance(component,ActorComponent)):
            self.actors.append(component)
            component.physics = component.parentEntity.GetComponent(PhysicsComponent)
    def OnDeleteComponent(self, component : Component): #Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        if(isinstance(component,ActorComponent)):
            self.actors.remove(component)
    def RegisterAction(self, name, func):
        self.actions[name] = func

    # Camera
    def CameraTick(self):
        newCameraPosition = MoveTowards(self.cameraPosition,self.cameraTarget.position,
                                        self.game.deltaTime*self.cameraSpeed/10 * Distance(self.cameraTarget.position,
                                                                                       self.cameraPosition)*0.15)
        self.cameraPosition[0] = newCameraPosition[0]
        self.cameraPosition[1] = newCameraPosition[1]

    # General Actor Actions
    def ActionMoveUp(self, actor: ActorComponent, currentScene: Scene):
        actor._movementThisTick[1] = -1
    def ActionMoveDown(self, actor : ActorComponent, currentScene : Scene):
        actor._movementThisTick[1] = 1
    def ActionMoveLeft(self, actor : ActorComponent, currentScene : Scene):
        actor._movementThisTick[0] = -1
    def ActionMoveRight(self, actor : ActorComponent, currentScene : Scene):
        actor._movementThisTick[0] = 1

    def ActorMovementTick(self, actor : ActorComponent):
        actor.physics.AddVelocity(
            (actor._movementThisTick[0] * actor.speed * self.game.deltaTime, actor._movementThisTick[1] * actor.speed * self.game.deltaTime))

    # Item Tick

    def ActorItemTick(self, actor : ActorComponent):
        if actor.heldItem:
            actor.heldItem.position = [actor.parentEntity.position[0],actor.parentEntity.position[1]+5]

    # Attack Actions
    def ActionAttack1(self, actor : ActorComponent, currentScene : Scene):
        # todo refactor, code here seems messy. Also it currently takes screen mouse position, wont work later.
        if(actor.heldItem):
            actor.heldItem.position = actor.parentEntity.position[:]
            actor.heldItem.GetComponent(SpriteRenderer).sprite.SetRotation(LookAt((0,0),
                                                                                   self.renderingSystem.screenMousePosition))
            gunComp : GunComponent = actor.heldItem.GetComponent(GunComponent)
            if(gunComp and gunComp.activeMagazineCount > 0 and time.time() - gunComp.lastShootTime >= gunComp.shootDelay):
                gunComp.activeMagazineCount -= 1
                gunComp.lastShootTime = time.time()
                gunComp.bulletPrefabFunc(currentScene)