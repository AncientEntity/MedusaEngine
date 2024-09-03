from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.sprites import Sprite
from engine.datatypes.timedevents import TimedEvent
from engine.ecs import Component, Entity
from game.prefabs.ui.UIHealthPrefab import UIHealthPrefabHandler


class ActorComponent(Component):
    def __init__(self):
        super().__init__()
        self.driver = None
        self.alive = True

        # Movement
        self._movementThisTick = [0,0]
        self.speed = 500
        self.physics : PhysicsComponent = None

        # Inventory
        self.heldItem : Entity = None
        self.destroyItemOnDeath = False

        # Animation
        self.spriteRenderer : SpriteRenderer = None
        self.hitEffectSprites : list[Sprite] = [] # Sprites in here get tinted on hit.
        self.hitEffectEvent : TimedEvent = None # The current hit effect event (coloured tint on hit).

        # Health/Damage
        self.friendly = False
        self.health = 100
        self.maxHealth = 100
        self.damageTint = (200,0,0)
        self.meleeDamage = 25
        self.meleeKnockbackForce = 80
        self.healthUI : UIHealthPrefabHandler = UIHealthPrefabHandler(self)


        self._lastDamageTime = 0
        self.postHitInvincibility = 0.25