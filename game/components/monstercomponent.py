from engine.datatypes.pathfinding import TilePathfinderHelper, TilemapPathfinder
from engine.ecs import Component
from game.components.playercomponent import PlayerComponent


class MonsterComponent(Component):
    def __init__(self):
        super().__init__()

        # Pathfinding/Movement
        self.movementSpeed = 50
        self.agroRange = 8 # If 0 or less, it will not pathfind.
        self.targetPlayer : PlayerComponent = None
        self.pathfinding : TilePathfinderHelper = None # Initialized inside MonsterSystem