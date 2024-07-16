import pygame

from engine.components.physicscomponent import PhysicsComponent
from engine.datatypes.sprites import AnimatedSprite, Sprite
from engine.datatypes.timedevents import TimedEvent
from engine.ecs import Component
from game import assets
from game.components.itemcomponent import ItemComponent


class PlayerComponent(Component):
    def __init__(self):
        super().__init__()
        self.speed = 500
        self.weapon : ItemComponent = None

        self.physics : PhysicsComponent = None
        self.playerRenderer = None
        self.cachedWeaponSpriteRef : Sprite = None

        self.lastDashTime = 0 # Last time the player dashed
        self.dashDelay = 0.75
        self.dashImpulseVelocity = 500
        self.dashTimedEvent : TimedEvent = None

        self.afterImages = [] # after image entities used for dashing.

        self.controls = {
            "up" : pygame.K_w,
            "down" : pygame.K_s,
            "left" : pygame.K_a,
            "right" : pygame.K_d,
            "dash" : pygame.K_LSHIFT
        }

        self.idleAnim = AnimatedSprite(
            [assets.dungeonTileSet["knight_f_idle_anim_f0"], assets.dungeonTileSet["knight_f_idle_anim_f1"],
             assets.dungeonTileSet["knight_f_idle_anim_f2"], assets.dungeonTileSet["knight_f_idle_anim_f3"]], 5)
        self.runAnim = AnimatedSprite(
            [assets.dungeonTileSet["knight_f_run_anim_f0"], assets.dungeonTileSet["knight_f_run_anim_f1"],
             assets.dungeonTileSet["knight_f_run_anim_f2"], assets.dungeonTileSet["knight_f_run_anim_f3"]], 8)