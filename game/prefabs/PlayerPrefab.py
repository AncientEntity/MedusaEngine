from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.scenes.levelscene import LevelScene
from game import assets
from game.components.itemcomponent import ItemComponent
from game.components.playercomponent import PlayerComponent
from game.systems.playersystem import PlayerSystem


def CreatePlayer(currentScene : LevelScene):
    playerComponent = PlayerComponent()
    spriteRenderer = SpriteRenderer(None)
    spriteRenderer.drawOrder = 50
    physicsComponent = PhysicsComponent()
    physicsComponent.mapToSpriteOnStart = False
    physicsComponent.friction = [10,10]
    physicsComponent.collidesWithLayers = [0]
    physicsComponent.bounds = [10,16]
    physicsComponent.offset = (0,6)
    physicsComponent.triggersWithLayers = [5]

    def OnTriggered(self : PhysicsComponent, other : PhysicsComponent):
        if("Item" in other.parentEntity.name):
            if (other == self.parentEntity.GetComponent(PlayerComponent).weapon):
                return # Already holding this item
            else:
                self.parentEntity.GetComponent(PlayerComponent).weapon = other.parentEntity.GetComponent(ItemComponent)
                currentScene.GetSystemByClass(PlayerSystem).cachedWeaponSpriteRef = None

    physicsComponent.onTriggerStart.append(OnTriggered)

    return currentScene.CreateEntity("Player",[0,0],components=[playerComponent,spriteRenderer,physicsComponent])