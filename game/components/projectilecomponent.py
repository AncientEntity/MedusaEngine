import math

from engine.components.physicscomponent import PhysicsComponent
from engine.ecs import Component

class ProjectileComponent(Component):
    def __init__(self, speed, rotation):
        super().__init__()
        self.damage = 8
        self.speed = speed
        self.speedRotation = rotation

        self.velocity = [self.speed * math.cos(math.radians(self.speedRotation)),
                               -self.speed * math.sin(math.radians(self.speedRotation))]

        self.physics : PhysicsComponent = None