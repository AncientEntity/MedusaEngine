from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.spritesheet import SpriteSheet
from engine.ecs import Scene
from engine.scenes.levelscene import LevelScene
from game.components.GeneratorComponent import GeneratorComponent
from game.components.ItemComponent import ItemComponent
import random

itemSpriteSheet = SpriteSheet("game/art/ryanitems.png",10)

def CreateItem(scene: Scene,itemID):
    physics = PhysicsComponent([5,5],(0,0))

    newEntity = scene.CreateEntity(name="Item", position=[0, 0], components=[SpriteRenderer(itemSpriteSheet[itemID]),ItemComponent(itemID),physics])
    return newEntity