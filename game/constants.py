from engine.datatypes.spritesheet import SpriteSheet
from game.datatypes.Placeable import Placeable

ConveyorPlaceable = Placeable("Conveyor Belt", [4,5,6,7],2)
UndergroundEntrance = Placeable("Underground Entrance", [12,13,14,15],5)
UndergroundExit = Placeable("Underground Exit", [20,21,22,23],5)

worldSpriteSheet = SpriteSheet("game/art/tilset.png",16)