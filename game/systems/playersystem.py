import asyncio
import math, time

from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.sprites import Sprite
from engine.ecs import EntitySystem, Scene, Component
from engine.engine import Input
from engine.systems.renderer import RenderingSystem
from engine.tools.math import MoveTowards, Distance, NormalizeVec
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
            self.Weapon(player)
    def Weapon(self, player : PlayerComponent):
        if player.weapon:
            player.weapon.parentEntity.position = [player.parentEntity.position[0]+3,player.parentEntity.position[1]+5]
            if(player.cachedWeaponSpriteRef == None):
                player.cachedWeaponSpriteRef : Sprite = player.weapon.parentEntity.GetComponent(SpriteRenderer).sprite
            if(self.renderingSystem.screenMousePosition[0] != 0):
                ang = -math.degrees(math.atan2(self.renderingSystem.screenMousePosition[1],self.renderingSystem.screenMousePosition[0]))
                player.cachedWeaponSpriteRef.SetRotation(ang)
                player.cachedWeaponSpriteRef.SetScale((1.5,1.5))
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
        if(time.time() - player.lastDashTime >= player.dashDelay):
            if(Input.KeyPressed(player.controls["dash"])):
                if(player.physics.velocity[0] == 0 and player.physics.velocity[1] == 0):
                    pass # Cant dash if not moving
                else:
                    normalizedVelocity = NormalizeVec(player.physics.velocity)
                    player.physics.velocity = [normalizedVelocity[0]*player.dashImpulseVelocity,normalizedVelocity[1]*player.dashImpulseVelocity]
                    player.lastDashTime = time.time()
                    player.playerRenderer.sprite.SetTint((255, 255, 255))
        elif(time.time() - player.lastDashTime >= player.dashDelay * 0.1):
            player.playerRenderer.sprite.SetTint(None)

        player.physics.AddVelocity((movement[0] * player.speed * self.game.deltaTime, movement[1] * player.speed * self.game.deltaTime))

        if(moving):
            player.playerRenderer.sprite = player.runAnim
        else:
            player.playerRenderer.sprite = player.idleAnim

        newCameraPosition = MoveTowards(self.cameraPosition,player.parentEntity.position,
                                        self.game.deltaTime*player.speed/10 * Distance(player.parentEntity.position,self.cameraPosition)*0.15)
        self.cameraPosition[0] = newCameraPosition[0]
        self.cameraPosition[1] = newCameraPosition[1]
    def OnEnable(self, currentScene : Scene):
        self.renderingSystem = currentScene.GetSystemByClass(RenderingSystem)
        self.cameraPosition = self.renderingSystem.cameraPosition
    def OnNewComponent(self,component : PlayerComponent): #Called when a new component is created into the scene. (Used to initialize that component)
        component.physics = component.parentEntity.GetComponent(PhysicsComponent)
        component.playerRenderer = component.parentEntity.GetComponent(SpriteRenderer)