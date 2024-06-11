import pygame

from engine.ecs import EntitySystem, Scene
from engine.engine import Input
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
    def Update(self, currentScene: Scene):
        for player in currentScene.components[PlayerComponent]:
            self.PlayerMovement(player)
            RenderingSystem.instance.cameraPosition = player.parentEntity.position

            if self.tintTest % 120 == 0:
                import random
                r = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                player.idleAnim.SetTint(r)
                player.runAnim.SetTint(r)
        if(self.tintTest >= 0):
            self.tintTest += 1
        if Input.KeyPressed(pygame.K_g):
            newSkeleton = prefabs.CreateSkeleton(currentScene)
            newSkeleton.position = [player.parentEntity.position[0],player.parentEntity.position[1]-100]
        if Input.KeyDown(pygame.K_q):
            if(self.tintTest == -1):
                self.tintTest = 0
            else:
                self.tintTest = -1
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
        if(Input.KeyDown(pygame.K_r)):
            self.game.LoadScene(sidescrollingscene.SideScrollingScene())
        if (Input.KeyDown(pygame.K_t) or player.parentEntity.position[1] >= 200):
            self.game.LoadScene(TiledTestScene())