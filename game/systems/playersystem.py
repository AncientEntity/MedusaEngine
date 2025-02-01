import pygame

from engine.datatypes.assetmanager import assets
from engine.datatypes.timedevents import TimedEvent
from engine.ecs import EntitySystem, Scene
from engine.engine import Input
from engine.networking.networkstate import NetworkState
from engine.systems import physics
from engine.systems.renderer import SpriteRenderer, RenderingSystem
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
        for player in currentScene.components[PlayerComponent]:
            self.PlayerMovement(player)
            if player.parentEntity.entityId == NetworkState.clientId:
                RenderingSystem.instance.cameraPosition = player.parentEntity.position

        if Input.KeyPressed(pygame.K_g):
            newSkeleton = assets.Instantiate("skeleton",currentScene)
            newSkeleton.position = [player.parentEntity.position[0],player.parentEntity.position[1]-100]
        if Input.KeyDown(pygame.K_q):
            if player.tintEvent == None:
                player.tintEvent = TimedEvent(self.DoTint,args=(player,),startDelay=0.25,repeatDelay=0.25,repeatCount=None)
                self.StartTimedEvent(player.tintEvent)
            else:
                player.tintEvent.repeatCount = 0
                player.tintEvent = None
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
            player.parentEntity.GetComponent(SpriteRenderer).sprite.SetFlipX(True)
            moved = True
        elif(Input.KeyPressed(player.controls["right"])):
            player.parentEntity.GetComponent(physics.PhysicsComponent).AddVelocity((self.game.deltaTime * player.speed,0))
            player.parentEntity.GetComponent(SpriteRenderer).sprite.SetFlipX(False)
            moved = True
        if(moved):
            RenderingSystem.instance.cameraPosition = player.parentEntity.position
            player.parentEntity.GetComponent(SpriteRenderer).sprite = player.runAnim
        else:
            player.parentEntity.GetComponent(SpriteRenderer).sprite = player.idleAnim

    def DoTint(self, player):
        import random
        r = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        player.idleAnim.SetTint(r)
        player.runAnim.SetTint(r)