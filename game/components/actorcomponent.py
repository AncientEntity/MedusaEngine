from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
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

        # Animation
        self.spriteRenderer : SpriteRenderer = None