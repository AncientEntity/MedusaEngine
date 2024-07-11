from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.ecs import Scene
from game import assets
from game.components.itemcomponent import ItemComponent


def CreateItemPrefab(itemID, currentScene : Scene):
    spriteRenderer = SpriteRenderer(assets.itemSheet[itemID])
    spriteRenderer.drawOrder = 100
    itemComponent = ItemComponent(itemID)
    physicsComponent = PhysicsComponent()
    physicsComponent.collidesWithLayers = []
    physicsComponent.triggersWithLayers = [0]
    physicsComponent.physicsLayer = 5


    return currentScene.CreateEntity("Item("+str(itemID)+")",[0,0],components=[spriteRenderer,itemComponent,physicsComponent])