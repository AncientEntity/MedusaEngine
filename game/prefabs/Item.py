from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.spritesheet import SpriteSheet
from engine.ecs import Scene
from game.components.ItemComponent import ItemComponent

itemSpriteSheet = SpriteSheet("game/art/ryanitems.png",10)

def CreateItem(scene: Scene,itemID):
    newEntity = scene.CreateEntity(name="Item", position=[0, 0], components=[SpriteRenderer(itemSpriteSheet[(itemID,0)]),ItemComponent(itemID)])
    return newEntity
