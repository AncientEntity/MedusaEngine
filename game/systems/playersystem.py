import asyncio
import math, time

from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.sprites import Sprite
from engine.datatypes.timedevents import TimedEvent
from engine.ecs import EntitySystem, Scene, Component
from engine.engine import Input
from engine.systems.renderer import RenderingSystem
from engine.tools.math import MoveTowards, Distance, NormalizeVec, LookAt, Magnitude
from game.components.actorcomponent import ActorComponent
from game.components.guncomponent import GunComponent
from game.components.playercomponent import PlayerComponent
import pygame

from game.systems.actorsystem import ActorSystem


class PlayerSystem(EntitySystem):
    def __init__(self):
        super().__init__([PlayerComponent]) #Put target components here

    def OnEnable(self, currentScene : Scene):
        currentScene.GetSystemByClass(ActorSystem).RegisterAction("dash",self.ActionPlayerDash)
    def Update(self,currentScene : Scene):
        for player in currentScene.components[PlayerComponent]:
            self.Animate(player)

    def Animate(self, player : PlayerComponent):

        moving = Magnitude(player.physics.velocity) > 0.1

        if(moving):
            player.playerRenderer.sprite = player.runAnim
            if(player.physics.velocity[0] > 0):
                player.playerRenderer.sprite.SetFlipX(False)
            else:
                player.playerRenderer.sprite.SetFlipX(True)
        else:
            player.playerRenderer.sprite = player.idleAnim

    def ActionPlayerDash(self, actor : ActorComponent, currentScene : Scene):
        self.Dash(actor.parentEntity.GetComponent(PlayerComponent)) # todo hashtable for actor->parent component in system.

    def Dash(self, player : PlayerComponent):
        timeSinceDash = time.time() - player.lastDashTime
        if(timeSinceDash >= player.dashDelay):
            if(player.physics.velocity[0] == 0 and player.physics.velocity[1] == 0):
                return # Cant dash if not moving
            else:
                normalizedVelocity = NormalizeVec(player.physics.velocity)
                player.physics.velocity = [normalizedVelocity[0]*player.dashImpulseVelocity,normalizedVelocity[1]*player.dashImpulseVelocity]
                player.lastDashTime = time.time()
                player.playerRenderer.sprite.SetTint((255, 255, 255))
                player.dashTimedEvent = TimedEvent(self.HandleAfterImages,(player,),0,0.025,3)
                self.StartTimedEvent(player.dashTimedEvent)
                for afterImage in player.afterImages:
                    afterImage.GetComponent(SpriteRenderer).sprite = None
    def OnNewComponent(self,component : PlayerComponent): #Called when a new component is created into the scene. (Used to initialize that component)
        component.physics = component.parentEntity.GetComponent(PhysicsComponent)
        component.playerRenderer = component.parentEntity.GetComponent(SpriteRenderer)
    @staticmethod
    def HandleAfterImages(player : PlayerComponent):
        curAfterImage = None
        for afterImage in player.afterImages:
            if(afterImage.GetComponent(SpriteRenderer).sprite == None):
                curAfterImage = afterImage
                break
        if(curAfterImage != None):
            curAfterImage.GetComponent(SpriteRenderer).sprite = player.runAnim
            curAfterImage.position = player.parentEntity.position[:]
        else:
            # Should be done, now remove after images and reset player tint.
            player.playerRenderer.sprite.SetTint(None)
            for afterImage in player.afterImages:
                afterImage.GetComponent(SpriteRenderer).sprite = None