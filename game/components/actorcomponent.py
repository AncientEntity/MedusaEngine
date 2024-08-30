from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.timedevents import TimedEvent
from engine.ecs import Component, Entity

class ActorComponent(Component):
    def __init__(self):
        super().__init__()
        self.driver = None

        # Movement
        self._movementThisTick = [0,0]
        self.speed = 500
        self.physics : PhysicsComponent = None

        # Inventory
        self.heldItem : Entity = None
        self.destroyItemOnDeath = False

        # Animation
        self.spriteRenderer : SpriteRenderer = None
        self.hitEffectEvent : TimedEvent = None # The current hit effect event (coloured tint on hit).

        # Health/Damage
        self.friendly = False
        self.health = 100
        self.maxHealth = 100
        self.damageTint = (200,0,0)
        self.meleeDamage = 25
        self.meleeKnockbackForce = 250

        self._lastDamageTime = 0
        self.postHitInvincibility = 0.25