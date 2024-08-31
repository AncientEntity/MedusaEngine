from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.sprites import Sprite
from engine.datatypes.timedevents import TimedEvent
from engine.ecs import EntitySystem, Scene, Component, Entity
from engine.engine import Input
from engine.systems.renderer import RenderingSystem
from engine.tools.math import MoveTowards, Distance, LookAt, NormalizeVec, MoveTowardsDelta, Clamp
from game.components.actorcomponent import ActorComponent
from game.components.guncomponent import GunComponent
import time

from game.components.itemcomponent import ItemComponent
from game.components.playercomponent import PlayerComponent
from game.components.projectilecomponent import ProjectileComponent
from game.drivers.playerdriver import PlayerDriver
from game.drivers.testaidriver import TestAIDriver

class ActorSystem(EntitySystem):
    def __init__(self):
        super().__init__([ActorComponent]) #Put target components here

        self.currentScene : Scene = None

        self.actors : list[ActorComponent] = []
        self.actions = {}

        # Register default actions
        self.RegisterAction("up", self.ActionMoveUp)
        self.RegisterAction("down", self.ActionMoveDown)
        self.RegisterAction("left", self.ActionMoveLeft)
        self.RegisterAction("right", self.ActionMoveRight)
        self.RegisterAction("attack1", self.ActionAttack1)
        self.RegisterAction("reload", self.ActionReload)

        # Rendering/Camera
        self.renderingSystem : RenderingSystem = None
        self.cameraTarget : Entity = None
        self.cameraPosition = None # Contains the same list that the rendering system has.
        self.cameraSpeed = 500

    def Update(self,currentScene : Scene):
        actor : ActorComponent
        for actor in self.actors:
            if not actor.driver or not actor.alive:
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
        self.currentScene = currentScene


    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        if(isinstance(component,ActorComponent)):
            self.actors.append(component)
            component.physics = component.parentEntity.GetComponent(PhysicsComponent)
            component.spriteRenderer = component.parentEntity.GetComponent(SpriteRenderer)
            component.physics.onTriggerStart.append(self.OnActorsInteract)
            component.physics.onTriggerStart.append(self.OnProjectileEnter)
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
            gunComp : GunComponent = actor.heldItem.GetComponent(GunComponent)
            if gunComp.isReloading:
                return

            weaponSprite = actor.heldItem.GetComponent(SpriteRenderer).sprite
            weaponRotation = LookAt(actor.parentEntity.position,actor.driver.targetPosition)+gunComp.spriteRotationOffset

            weaponSprite.SetRotation(weaponRotation)
            if gunComp.spriteRotateHalf:
                shouldFlip = True if weaponRotation <= -45 or weaponRotation >= 145 else False
                weaponSprite.SetFlipY(shouldFlip)
                weaponSprite.SetFlipX(shouldFlip)

            if(gunComp and gunComp.ammo > 0 and time.time() - gunComp.lastShootTime >= gunComp.shootDelay):
                gunComp.ammo -= 1
                gunComp.lastShootTime = time.time()
                gunComp.bulletPrefabFunc(currentScene)

    def OnProjectileEnter(self, me : PhysicsComponent, other : PhysicsComponent):
        projectile : ProjectileComponent = other.parentEntity.GetComponent(ProjectileComponent)
        meActor : ActorComponent = me.parentEntity.GetComponent(ActorComponent) #todo remove GetComponent.
        if projectile and projectile.friendly != meActor.friendly and time.time() - meActor._lastDamageTime >= meActor.postHitInvincibility:
            normalizedKnockback = NormalizeVec(projectile.velocity)
            knockbackForce = (
                normalizedKnockback[0] * projectile.knockbackForce, normalizedKnockback[1] * projectile.knockbackForce)
            self.DoDamage(meActor, projectile.damage, knockbackForce)
            self.currentScene.DeleteEntity(other.parentEntity)

    def OnActorsInteract(self, me : PhysicsComponent, other : PhysicsComponent):
        meActor : ActorComponent = me.parentEntity.GetComponent(ActorComponent)
        otherActor : ActorComponent = other.parentEntity.GetComponent(ActorComponent)
        if not meActor or not otherActor or not otherActor.alive:
            return
        if otherActor.meleeDamage > 0:
            normalizedKnockback = NormalizeVec((meActor.parentEntity.position[0]-otherActor.parentEntity.position[0],
                                                meActor.parentEntity.position[1]-otherActor.parentEntity.position[1]))
            knockbackForce = (
                normalizedKnockback[0] * otherActor.meleeKnockbackForce, normalizedKnockback[1] * otherActor.meleeKnockbackForce)
            self.DoDamage(meActor, otherActor.meleeDamage, knockbackForce)

    def DoDamage(self, actor : ActorComponent, damageAmount : int, knockbackVelocity):
        actor.health -= damageAmount
        actor._lastDamageTime = time.time()
        self.HitEffect(actor,True)
        actor.hitEffectEvent = TimedEvent(self.HitEffect,
                                            args=(actor,False),
                                            startDelay=actor.postHitInvincibility,
                                            repeatDelay=0,
                                            repeatCount=1)
        self.StartTimedEvent(actor.hitEffectEvent)
        if (actor.health <= 0):
            # Delayed actor delete, and disable driver. So it still has the hit effect event.
            delayedDeleteEvent = TimedEvent(self.currentScene.DeleteEntity,
                       args=(actor.parentEntity,),
                       startDelay=0.25,
                       repeatDelay=0,
                       repeatCount=1)
            actor.alive = False
            self.StartTimedEvent(delayedDeleteEvent)

            if actor.physics:
                actor.physics.velocity = [0,0]
                actor.physics.physicsLayer = -1

            # Delete heldItem if actor.destroyItemOnDeath
            if actor.heldItem:
                actor.heldItem.GetComponent(ItemComponent).held = False
                if actor.destroyItemOnDeath:
                    self.currentScene.DeleteEntity(actor.heldItem)
        else:
            actor.physics.AddVelocity(knockbackVelocity)

    # todo redo this to have a give tint/remove tint event. Prevents other things from effecting the logic...
    def HitEffect(self, actor : ActorComponent, enable):
        for sprite in actor.hitEffectSprites:
            if(enable):
                sprite.SetTint(actor.damageTint)
            else:
                sprite.SetTint(None)

    # Reloading
    def ActionReload(self, actor : ActorComponent, currentScene : Scene):
        if not actor.heldItem:
            return

        gun : GunComponent = actor.heldItem.GetComponent(GunComponent)
        if gun:
            if gun.isReloading or gun.ammo >= gun.ammoPerMagazine:
                return

            gun.ammo = 0
            reloadEvent = TimedEvent(self.FinishReload,(gun,),gun.reloadTime,1,1)
            self.StartTimedEvent(reloadEvent)
            gun.isReloading = True

    def FinishReload(self, gun : GunComponent):
        gun.isReloading = False
        ammoToAdd = Clamp(gun.ammoPerMagazine - gun.ammo, 0, gun.ammoReserves)
        gun.ammo += ammoToAdd
        gun.ammoReserves -= ammoToAdd