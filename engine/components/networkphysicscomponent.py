from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.ecs import Component
from engine.logging import LOG_WARNINGS, Log
from engine.networking.variables.networkvarvector import NetworkVarVector
from engine.networking.variables.networkvarvectori import NetworkVarVectorInterpolate
from engine.tools.math import Magnitude


class NetworkPhysicsComponent(PhysicsComponent):
    def __init__(self,bounds=[10,10],gravity=(0,0)):
        super().__init__(bounds, gravity)
        self._velocity = NetworkVarVectorInterpolate([0,0])
        self._velocity.interpolateMaxDistance = 15
        self._velocity.interpolateSpeed = 12
        self._velocity.serverAuthorityRequired = True

    def get_velocity(self):
        return self._velocity.Get()
    def set_velocity(self, value):
        self._velocity.Set(value)
    def get_speed(self):
        return Magnitude(self._velocity.Get())

    velocity = property(get_velocity,
                                 set_velocity)

    def AddVelocity(self,impulse):
        self._velocity.Add(impulse)