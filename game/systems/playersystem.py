import pygame

from engine.datatypes.assetmanager import assets
from engine.datatypes.timedevents import TimedEvent
from engine.ecs import EntitySystem, Scene
from engine.engine import Input
from engine.networking.networkstate import NetworkState
from engine.networking.rpc import RPC
from engine.systems import physics
from engine.systems.renderer import SpriteRenderer, RenderingSystem
from engine.tools.math import Magnitude
from game import prefabs
from game.components.playercomponent import PlayerComponent
from game.scenes import sidescrollingscene
from game.scenes.tiledtestscene import TiledTestScene

class PlayerSystem(EntitySystem):
    def __init__(self):
        super().__init__([PlayerComponent])
        self.tintTest = -1
    def OnEnable(self, currentScene : Scene):
        for player in self.game.GetCurrentScene().components[PlayerComponent]:
            player.parentEntity.GetComponent(SpriteRenderer).sprite = player.idleAnim
    def OnNewComponent(self,component : PlayerComponent):
        component.parentEntity.GetComponent(SpriteRenderer).sprite = component.idleAnim
    def Update(self, currentScene: Scene):
        player : PlayerComponent
        for player in currentScene.components[PlayerComponent]:
            if player.parentEntity.ownerId == NetworkState.clientId or not NetworkState.identity:
                self.PlayerMovement(player)
                RenderingSystem.instance.cameraPosition = player.parentEntity.position

                if Input.KeyDown(pygame.K_q):
                    if player.tintEvent == None:
                        player.tintEvent = TimedEvent(self.WrappedDoTint, args=(), startDelay=0.25, repeatDelay=0.25,
                                                      repeatCount=None)
                        self.StartTimedEvent(player.tintEvent)
                    else:
                        player.tintEvent.repeatCount = 0
                        player.tintEvent = None

            velocity = player.parentEntity.GetComponent(physics.PhysicsComponent).velocity
            if Magnitude(velocity) >= 10:
                player.parentEntity.GetComponent(SpriteRenderer).sprite = player.runAnim
                player.runAnim.SetFlipX(velocity[0] < 0)
                player.idleAnim.SetFlipX(velocity[0] < 0)
            else:
                player.parentEntity.GetComponent(SpriteRenderer).sprite = player.idleAnim

        if Input.KeyPressed(pygame.K_g):
            newSkeleton = assets.NetInstantiate("skeleton",currentScene)
            newSkeleton.position = [player.parentEntity.position[0],player.parentEntity.position[1]-100]

        if(Input.KeyDown(pygame.K_r)):
            self.game.LoadScene(sidescrollingscene.SideScrollingScene)
        if (Input.KeyDown(pygame.K_t)):
            self.game.LoadScene(TiledTestScene)
    def PlayerMovement(self,player : PlayerComponent):
        moved = False
        if (Input.KeyPressed(player.controls["up"]) and player.parentEntity.GetComponent(physics.PhysicsComponent).touchingDirections['bottom']):
            player.parentEntity.GetComponent(physics.PhysicsComponent).velocity[1] -= 200
            moved = True
        if (Input.KeyPressed(player.controls["left"])):
            player.parentEntity.GetComponent(physics.PhysicsComponent).AddVelocity((-self.game.deltaTime * player.speed,0))
            moved = True
        elif(Input.KeyPressed(player.controls["right"])):
            player.parentEntity.GetComponent(physics.PhysicsComponent).AddVelocity((self.game.deltaTime * player.speed,0))
            moved = True
        if(moved):
            RenderingSystem.instance.cameraPosition = player.parentEntity.position

    def WrappedDoTint(self):
        import random
        r = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.DoTint(NetworkState.clientId, r)

    @RPC(serverOnly=False)
    def DoTint(self, playerIndex, color):
        for player in self.game.GetCurrentScene().components[PlayerComponent]:
            if player.parentEntity.ownerId == playerIndex:
                break

        player.idleAnim.SetTint(color)
        player.runAnim.SetTint(color)