import pygame

from engine.ecs import EntitySystem, Component, Scene
from engine.engine import Input
from engine.systems.renderer import SpriteRenderer, RenderingSystem, AnimatedSprite
from engine.tools.spritesheet import SpriteSheet
from game import assets
from game.scenes import levelscene


class PlayerComponent(Component):
    def __init__(self):
        super().__init__()
        self.controls = {'up' : pygame.K_w, 'down' : pygame.K_s, 'left' : pygame.K_a, 'right' : pygame.K_d}
        self.speed = 85

        self.idleAnim = AnimatedSprite(
            [assets.dungeonTileSet["knight_f_idle_anim_f0"], assets.dungeonTileSet["knight_f_idle_anim_f1"],
             assets.dungeonTileSet["knight_f_idle_anim_f2"], assets.dungeonTileSet["knight_f_idle_anim_f3"]], 5)
        self.runAnim = AnimatedSprite(
            [assets.dungeonTileSet["knight_f_run_anim_f0"], assets.dungeonTileSet["knight_f_run_anim_f1"],
             assets.dungeonTileSet["knight_f_run_anim_f2"], assets.dungeonTileSet["knight_f_run_anim_f3"]], 8)

class PlayerSystem(EntitySystem):
    def __init__(self):
        super().__init__([PlayerComponent])
    def OnEnable(self):
        for player in self.game.GetCurrentScene().components[PlayerComponent]:
            player.parentEntity.GetComponent(SpriteRenderer).sprite = player.idleAnim
            RenderingSystem.instance.cameraPosition = player.parentEntity.position
    def Update(self, currentScene: Scene):
        for player in currentScene.components[PlayerComponent]:
            self.PlayerMovement(player)
    def PlayerMovement(self,player : PlayerComponent):
        moved = False
        if (Input.KeyPressed(player.controls["up"])):
            player.parentEntity.position[1] -= self.game.deltaTime * player.speed
            moved = True
        elif(Input.KeyPressed(player.controls["down"])):
            player.parentEntity.position[1] += self.game.deltaTime * player.speed
            moved = True
        if (Input.KeyPressed(player.controls["left"])):
            player.parentEntity.position[0] -= self.game.deltaTime * player.speed
            player.parentEntity.GetComponent(SpriteRenderer).sprite.FlipX(True)
            moved = True
        elif(Input.KeyPressed(player.controls["right"])):
            player.parentEntity.position[0] += self.game.deltaTime * player.speed
            player.parentEntity.GetComponent(SpriteRenderer).sprite.FlipX(False)
            moved = True
        if(moved):
            RenderingSystem.instance.cameraPosition = player.parentEntity.position
            player.parentEntity.GetComponent(SpriteRenderer).sprite = player.runAnim
        else:
            player.parentEntity.GetComponent(SpriteRenderer).sprite = player.idleAnim