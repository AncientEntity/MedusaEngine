import pygame

from engine.ecs import EntitySystem, Scene
from engine.engine import Input
from engine.systems import physics
from engine.systems.renderer import SpriteRenderer, RenderingSystem
from game.components.playercomponent import PlayerComponent
from game.scenes import sidescrollingscene
from game.scenes.tiledtestscene import TiledTestScene

class PlayerSystem(EntitySystem):
    def __init__(self):
        super().__init__([PlayerComponent])
    def OnEnable(self):
        for player in self.game.GetCurrentScene().components[PlayerComponent]:
            player.parentEntity.GetComponent(SpriteRenderer).sprite = player.idleAnim
    def Update(self, currentScene: Scene):
        for player in currentScene.components[PlayerComponent]:
            self.PlayerMovement(player)
            RenderingSystem.instance.cameraPosition = player.parentEntity.position
    def PlayerMovement(self,player : PlayerComponent):
        moved = False
        if (Input.KeyDown(player.controls["up"]) and player.parentEntity.GetComponent(physics.PhysicsComponent).touchingDirections['bottom']):
            player.parentEntity.GetComponent(physics.PhysicsComponent).velocity[1] -= 200
            moved = True
        if (Input.KeyPressed(player.controls["left"])):
            player.parentEntity.GetComponent(physics.PhysicsComponent).AddVelocity((-self.game.deltaTime * player.speed,0))
            player.parentEntity.GetComponent(SpriteRenderer).sprite.FlipX(True)
            moved = True
        elif(Input.KeyPressed(player.controls["right"])):
            player.parentEntity.GetComponent(physics.PhysicsComponent).AddVelocity((self.game.deltaTime * player.speed,0))
            player.parentEntity.GetComponent(SpriteRenderer).sprite.FlipX(False)
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