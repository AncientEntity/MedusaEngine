from engine.components.physicscomponent import PhysicsComponent
from engine.datatypes.pathfinding import TilemapPathfinder, TilePathfinderHelper
from engine.datatypes.timedevents import TimedEvent
from engine.ecs import EntitySystem, Scene, Component
from engine.scenes.levelscene import LevelScene
from engine.tools.math import Distance, MoveTowards, MoveTowardsDelta
from game.components.monstercomponent import MonsterComponent
from game.components.playercomponent import PlayerComponent


class MonsterSystem(EntitySystem):
    def __init__(self):
        super().__init__([MonsterComponent]) #Put target components here

        self.currentScene : LevelScene = None
        self.pathfindingEvent : TimedEvent = None
    def Update(self,currentScene : Scene):
        for monster in currentScene.components[MonsterComponent]:
            if not monster.pathfinding.cachedWorldPath or len(monster.pathfinding.cachedWorldPath) <= 2:
                continue
            moveDelta = MoveTowardsDelta(monster.parentEntity.position,
                                                        monster.pathfinding.cachedWorldPath[2],
                                                        monster.movementSpeed * self.game.deltaTime)
            monster.parentEntity.GetComponent(PhysicsComponent).Move(moveDelta)

    def OnEnable(self, currentScene : Scene):
        self.currentScene = currentScene

        self.pathfindingEvent = TimedEvent(self.DoPathfinding, args=(currentScene,), startDelay=0.1, repeatDelay=0.1, repeatCount=None)
        self.StartTimedEvent(self.pathfindingEvent)
    def OnNewComponent(self,component : MonsterComponent): #Called when a new component is created into the scene. (Used to initialize that component)
        pathfinder = TilemapPathfinder(list(self.currentScene.tileMapLayersByName.values()),[0])
        pathfinder.allowDiagonalMovement = False
        component.pathfinding = TilePathfinderHelper(pathfinder)
    def OnDeleteComponent(self, component : Component): #Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        pass
    def DoPathfinding(self, currentScene : LevelScene):
        monster : MonsterComponent
        for monster in currentScene.components[MonsterComponent]:
            if(monster.agroRange <= 0):
                continue # No agro range, dont pathfind.

            monster.targetPlayer = self.GetNearestPlayer(monster.parentEntity.position,currentScene)
            monster.pathfinding.SolveWorld(monster.parentEntity.position,monster.targetPlayer.parentEntity.position)

    def GetNearestPlayer(self, position, currentScene : Scene):
        nearest = None
        distance = 9999999 # Should be bigger than any map...
        for player in currentScene.components[PlayerComponent]:
            dis = Distance(position,player.parentEntity.position)
            if(dis <= distance):
                distance = dis
                nearest = player
        return nearest