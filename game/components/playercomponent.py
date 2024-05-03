from engine.ecs import Component
import pygame

from engine.systems.renderer import AnimatedSprite
from game import assets


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
