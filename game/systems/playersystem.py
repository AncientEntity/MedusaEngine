import math

from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.sprites import Sprite
from engine.ecs import EntitySystem, Scene, Component
from engine.engine import Input
from engine.systems.renderer import RenderingSystem
from engine.tools.math import MoveTowards, Distance
from game.components.playercomponent import PlayerComponent
import pygame

class PlayerSystem(EntitySystem):
    def __init__(self):
        super().__init__([PlayerComponent]) #Put target components here
        self.player : PlayerComponent = None
        self.physics : PhysicsComponent = None
        self.playerRenderer : SpriteRenderer = None

        self.renderingSystem : RenderingSystem = None

        self.cameraPosition = None # Contains the same list that the rendering system has.
        self.cachedWeaponSpriteRef : Sprite = None
    def Update(self,currentScene : Scene):
        self.Movement()
        self.Weapon()
    def Weapon(self):
        if self.player.weapon:
            self.player.weapon.parentEntity.position = [self.player.parentEntity.position[0]+3,self.player.parentEntity.position[1]+5]
            if(self.cachedWeaponSpriteRef == None):
                self.cachedWeaponSpriteRef : Sprite = self.player.weapon.parentEntity.GetComponent(SpriteRenderer).sprite
            if(self.renderingSystem.screenMousePosition[0] != 0):
                ang = -math.degrees(math.atan2(self.renderingSystem.screenMousePosition[1],self.renderingSystem.screenMousePosition[0]))
                self.cachedWeaponSpriteRef.SetRotation(ang)
                self.cachedWeaponSpriteRef.SetScale((1.5,1.5))
    def Movement(self):
        moving = False
        movement = [0,0]
        if(Input.KeyPressed(pygame.K_w)):
            movement[1] = -1
            moving = True
        elif(Input.KeyPressed(pygame.K_s)):
            movement[1] = 1
            moving = True
        if(Input.KeyPressed(pygame.K_a)):
            movement[0] = -1
            moving = True
            self.playerRenderer.sprite.SetFlipX(True)
        elif(Input.KeyPressed(pygame.K_d)):
            movement[0] = 1
            self.playerRenderer.sprite.SetFlipX(False)
            moving = True

        self.physics.AddVelocity((movement[0] * self.player.speed * self.game.deltaTime, movement[1] * self.player.speed * self.game.deltaTime))

        if(moving):
            self.playerRenderer.sprite = self.player.runAnim
        else:
            self.playerRenderer.sprite = self.player.idleAnim

        newCameraPosition = MoveTowards(self.cameraPosition,self.player.parentEntity.position,
                                        self.game.deltaTime*self.player.speed/10 * Distance(self.player.parentEntity.position,self.cameraPosition)*0.15)
        self.cameraPosition[0] = newCameraPosition[0]
        self.cameraPosition[1] = newCameraPosition[1]
    def OnEnable(self, currentScene : Scene):
        self.renderingSystem = currentScene.GetSystemByClass(RenderingSystem)
        self.cameraPosition = self.renderingSystem.cameraPosition
    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        self.player = component
        self.physics = self.player.parentEntity.GetComponent(PhysicsComponent)
        self.playerRenderer = self.player.parentEntity.GetComponent(SpriteRenderer)
    def OnDeleteComponent(self, component : Component): #Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        self.player = None