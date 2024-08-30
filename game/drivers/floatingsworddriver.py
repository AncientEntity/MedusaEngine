from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.pathfinding import TilePathfinderHelper
from engine.ecs import Scene
from engine.tools.math import Distance, MoveTowardsDelta, LookAt
from game.components.actorcomponent import ActorComponent
from game.components.playercomponent import PlayerComponent
from game.drivers.driverbase import DriverBase
import time


class FloatingSwordDriver(DriverBase):
    def __init__(self):
        super().__init__()

        # Movement
        self.agroRange = 240
        self.pathfinder : TilePathfinderHelper = None # Must be set in prefab.
        self.moveDelta = None

        self.lastMoveUpdate = time.time()
        self.moveUpdateDelay = 2
        self.spinDuration = 1
        self.finalSpinRotation = 0


        # Animations
        self.animations = {}
    def Update(self, actor : ActorComponent, currentScene : Scene):
        # Pathfinding

        timeSince = time.time() - self.lastMoveUpdate

        if timeSince >= self.moveUpdateDelay+self.spinDuration:
            lastClosestPlayer = self.ClosestPlayer(actor, currentScene)
            if lastClosestPlayer:
                self.moveDelta = MoveTowardsDelta(actor.parentEntity.position,
                                                  lastClosestPlayer.parentEntity.position,
                                                  1)
                self.finalSpinRotation = int(
                    LookAt(actor.parentEntity.position, lastClosestPlayer.parentEntity.position)-45) % 360
                actor.parentEntity.GetComponent(PhysicsComponent).AddVelocity((self.moveDelta[0] * actor.speed,
                                                                               self.moveDelta[1] * actor.speed))
            self.lastMoveUpdate = time.time()
        elif timeSince >= self.moveUpdateDelay or actor.spriteRenderer.sprite._rotation != self.finalSpinRotation:
            print(actor.spriteRenderer.sprite._rotation,self.finalSpinRotation)
            if actor.spriteRenderer.sprite._rotation == None:
                actor.spriteRenderer.sprite._rotation = 0
            actor.spriteRenderer.sprite.SetRotation((actor.spriteRenderer.sprite._rotation + 1) % 360)
            return



    def ClosestPlayer(self, actor : ActorComponent, currentScene : Scene):
        closest = None
        distance = None
        player : PlayerComponent
        for player in currentScene.components[PlayerComponent]:
            dist = Distance(actor.parentEntity.position,player.parentEntity.position)
            if (not distance or dist < distance) and dist <= self.agroRange:
                closest = player
                distance = dist
        return closest
