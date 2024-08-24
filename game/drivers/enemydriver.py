from engine.datatypes.pathfinding import TilePathfinderHelper
from engine.ecs import Scene
from engine.tools.math import Distance, MoveTowardsDelta
from game.components.actorcomponent import ActorComponent
from game.components.playercomponent import PlayerComponent
from game.drivers.driverbase import DriverBase
import time


class EnemyDriver(DriverBase):
    def __init__(self):
        super().__init__()
        self.inputs["up"] = self.GetUp
        self.inputs["down"] = self.GetDown
        self.inputs["left"] = self.GetLeft
        self.inputs["right"] = self.GetRight
        self.inputs["attack1"] = lambda : self.lastClosestPlayer != None # todo attacking
        self.inputs["reload"] = self.ShouldReload # todo attacking

        # Movement
        self.agroRange = 120
        self.pathfinder : TilePathfinderHelper = None # Must be set in prefab.
        self.moveDelta = None

        # Animation
        self.animations = {
            "idle" : None,
            "side" : None,
        }

        self.lastClosestPlayer = None
        self.lastReloadAttempt = time.time()

    def GetUp(self):
        return self.moveDelta and self.moveDelta[1] < 0
    def GetDown(self):
        return self.moveDelta and self.moveDelta[1] > 0
    def GetLeft(self):
        return self.moveDelta and self.moveDelta[0] < 0
    def GetRight(self):
        return self.moveDelta and self.moveDelta[0] > 0

    def Update(self, actor : ActorComponent, currentScene : Scene):
        # Pathfinding
        self.lastClosestPlayer = self.ClosestPlayer(actor, currentScene)
        if self.lastClosestPlayer:
            self.pathfinder.SolveWorld(actor.parentEntity.position,self.lastClosestPlayer.parentEntity.position)
            if self.pathfinder.cachedWorldPath and len(self.pathfinder.cachedWorldPath) > 2:
                self.moveDelta = MoveTowardsDelta(actor.parentEntity.position,
                                             self.pathfinder.cachedWorldPath[1],
                                             1)
            self.targetPosition = self.lastClosestPlayer.parentEntity.position[:]

        # Animation
        if actor.spriteRenderer:
            # Idle check
            if self.pathfinder.cachedWorldPath and len(self.pathfinder.cachedWorldPath) <= 2:
                if self.animations["idle"]:
                    actor.spriteRenderer.sprite = self.animations["idle"]
            elif self.moveDelta:
                if self.moveDelta[0] < -0.1 and self.animations["side"]:
                    actor.spriteRenderer.sprite = self.animations["side"]
                    self.animations["side"].SetFlipX(True)
                elif self.moveDelta[0] > 0.1 and self.animations["side"]:
                    actor.spriteRenderer.sprite = self.animations["side"]
                    self.animations["side"].SetFlipX(False)

    def ClosestPlayer(self, actor : ActorComponent, currentScene : Scene):
        closest = None
        distance = None
        player : PlayerComponent
        for player in currentScene.components[PlayerComponent]:
            dist = Distance(actor.parentEntity.position,player.parentEntity.position)
            if (distance == None or dist < distance) and dist <= self.agroRange:
                closest = player
                distance = dist
        return closest

    def ShouldReload(self):
        curTime = time.time()
        if curTime - self.lastReloadAttempt > 3 or self.lastClosestPlayer == None:
            self.lastReloadAttempt = curTime
            return True
        return False
