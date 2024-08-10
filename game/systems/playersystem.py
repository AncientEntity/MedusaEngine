import asyncio
import math, time

from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.sprites import Sprite
from engine.datatypes.timedevents import TimedEvent
from engine.ecs import EntitySystem, Scene, Component
from engine.engine import Input
from engine.systems.renderer import RenderingSystem
from engine.tools.math import MoveTowards, Distance, NormalizeVec, LookAt
from game.components.GunComponent import GunComponent
from game.components.playercomponent import PlayerComponent
import pygame

class PlayerSystem(EntitySystem):
    def __init__(self):
        super().__init__([PlayerComponent]) #Put target components here

        self.renderingSystem : RenderingSystem = None

        self.cameraPosition = None # Contains the same list that the rendering system has.
    def Update(self,currentScene : Scene):
        for player in currentScene.components[PlayerComponent]:
            self.Movement(player)
            self.Weapon(currentScene, player)
    def Weapon(self,currentScene : Scene, player : PlayerComponent):
        if(player.heldItem):
            player.heldItem.position = player.parentEntity.position[:]
            player.heldItem.GetComponent(SpriteRenderer).sprite.SetRotation(LookAt((0,0),
                                                                                   self.renderingSystem.screenMousePosition))
            if(Input.MouseButtonPressed(0)):
                gunComp : GunComponent = player.heldItem.GetComponent(GunComponent)
                if(gunComp and gunComp.activeMagazineCount > 0 and time.time() - gunComp.lastShootTime >= gunComp.shootDelay):
                    gunComp.activeMagazineCount -= 1
                    gunComp.lastShootTime = time.time()
                    gunComp.bulletPrefabFunc(currentScene)

    def Movement(self, player : PlayerComponent):
        moving = False
        movement = [0,0]
        if(Input.KeyPressed(player.controls["up"])):
            movement[1] = -1
            moving = True
        elif(Input.KeyPressed(player.controls["down"])):
            movement[1] = 1
            moving = True
        if(Input.KeyPressed(player.controls["left"])):
            movement[0] = -1
            moving = True
            player.playerRenderer.sprite.SetFlipX(True)
        elif(Input.KeyPressed(player.controls["right"])):
            movement[0] = 1
            player.playerRenderer.sprite.SetFlipX(False)
            moving = True

        self.Dash(player)

        player.physics.AddVelocity((movement[0] * player.speed * self.game.deltaTime, movement[1] * player.speed * self.game.deltaTime))

        if(moving):
            player.playerRenderer.sprite = player.runAnim
        else:
            player.playerRenderer.sprite = player.idleAnim

        newCameraPosition = MoveTowards(self.cameraPosition,player.parentEntity.position,
                                        self.game.deltaTime*player.speed/10 * Distance(player.parentEntity.position,self.cameraPosition)*0.15)
        self.cameraPosition[0] = newCameraPosition[0]
        self.cameraPosition[1] = newCameraPosition[1]
    def Dash(self, player : PlayerComponent):
        timeSinceDash = time.time() - player.lastDashTime
        if(timeSinceDash >= player.dashDelay):
            if(Input.KeyPressed(player.controls["dash"])):
                if(player.physics.velocity[0] == 0 and player.physics.velocity[1] == 0):
                    pass # Cant dash if not moving
                else:
                    normalizedVelocity = NormalizeVec(player.physics.velocity)
                    player.physics.velocity = [normalizedVelocity[0]*player.dashImpulseVelocity,normalizedVelocity[1]*player.dashImpulseVelocity]
                    player.lastDashTime = time.time()
                    player.playerRenderer.sprite.SetTint((255, 255, 255))
                    player.dashTimedEvent = TimedEvent(self.HandleAfterImages,(player,),0,0.025,3)
                    self.StartTimedEvent(player.dashTimedEvent)
                    for afterImage in player.afterImages:
                        afterImage.GetComponent(SpriteRenderer).sprite = None
        elif(timeSinceDash >= player.dashDelay * 0.1):
            player.playerRenderer.sprite.SetTint(None)
            for afterImage in player.afterImages:
                afterImage.GetComponent(SpriteRenderer).sprite = None

        #if(player.dashTimedEvent != None):
        #    result = player.dashTimedEvent.Tick()
        #    if not result:
        #        player.dashTimedEvent = None

    def OnEnable(self, currentScene : Scene):
        self.renderingSystem = currentScene.GetSystemByClass(RenderingSystem)
        self.cameraPosition = self.renderingSystem.cameraPosition
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