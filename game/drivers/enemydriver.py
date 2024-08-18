import pygame

from engine.datatypes.pathfinding import TilePathfinderHelper
from engine.ecs import Scene
from engine.engine import Input
from engine.tools.math import Distance, MoveTowardsDelta
from game.components.actorcomponent import ActorComponent
from game.components.playercomponent import PlayerComponent
from game.drivers.driverbase import DriverBase


class EnemyDriver(DriverBase):
    def __init__(self):
        super().__init__()
        self.inputs["up"] = self.GetUp
        self.inputs["down"] = self.GetDown
        self.inputs["left"] = self.GetLeft
        self.inputs["right"] = self.GetRight
        self.inputs["attack1"] = None # todo attacking

        self.pathfinder : TilePathfinderHelper = None # Must be set in prefab.

        self.moveDelta = None

    def GetUp(self):
        return self.moveDelta and self.moveDelta[1] < 0
    def GetDown(self):
        return self.moveDelta and self.moveDelta[1] > 0
    def GetLeft(self):
        return self.moveDelta and self.moveDelta[0] < 0
    def GetRight(self):
        return self.moveDelta and self.moveDelta[0] > 0

    def Update(self, actor : ActorComponent, currentScene : Scene):
        closestPlayer = self.ClosestPlayer(actor, currentScene)
        if closestPlayer:
            self.pathfinder.SolveWorld(actor.parentEntity.position,closestPlayer.parentEntity.position)
            if self.pathfinder.cachedWorldPath and len(self.pathfinder.cachedWorldPath) > 2:
                self.moveDelta = MoveTowardsDelta(actor.parentEntity.position,
                                             self.pathfinder.cachedWorldPath[1],
                                             1)


    def ClosestPlayer(self, actor : ActorComponent, currentScene : Scene):
        closest = None
        distance = None
        player : PlayerComponent
        for player in currentScene.components[PlayerComponent]:
            dist = Distance(actor.parentEntity.position,player.parentEntity.position)
            if distance == None or distance > dist:
                closest = player
                distance = dist
        return closest