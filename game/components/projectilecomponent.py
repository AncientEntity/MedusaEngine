import math, time

from engine.components.physicscomponent import PhysicsComponent
from engine.ecs import Component

class ProjectileComponent(Component):
    def __init__(self, speed, rotation, friendly):
        super().__init__()
        self.damage = 30
        self.knockbackForce = 200
        self.speed = speed
        self.speedRotation = rotation
        self.friendly = friendly

        self.velocity = [self.speed * math.cos(math.radians(self.speedRotation)),
                               -self.speed * math.sin(math.radians(self.speedRotation))]

        self.startTime = time.time()
        self.maxLifetime = 5