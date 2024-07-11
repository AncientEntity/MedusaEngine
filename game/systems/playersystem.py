from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
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

        self.cameraPosition = None
    def Update(self,currentScene : Scene):
        self.Movement()
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
                                        self.game.deltaTime*self.player.speed/10 * Distance(self.player.parentEntity.position,self.cameraPosition)*0.2)
        self.cameraPosition[0] = newCameraPosition[0]
        self.cameraPosition[1] = newCameraPosition[1]
    def OnEnable(self, currentScene : Scene):
        self.cameraPosition = currentScene.GetSystemByClass(RenderingSystem).cameraPosition
    def OnNewComponent(self,component : Component): #Called when a new component is created into the scene. (Used to initialize that component)
        self.player = component
        self.physics = self.player.parentEntity.GetComponent(PhysicsComponent)
        self.playerRenderer = self.player.parentEntity.GetComponent(SpriteRenderer)
    def OnDeleteComponent(self, component : Component): #Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        self.player = None