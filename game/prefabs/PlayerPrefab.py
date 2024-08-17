from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.sprites import AnimatedSprite
from engine.scenes.levelscene import LevelScene
from game import assets
from game.components.actorcomponent import ActorComponent
from game.components.itemcomponent import ItemComponent
from game.components.playercomponent import PlayerComponent
from game.drivers.playerdriver import PlayerDriver


def CreatePlayer(currentScene : LevelScene):

    actorComponent = ActorComponent()
    actorComponent.driver = PlayerDriver()

    playerComponent = PlayerComponent()

    spriteRenderer = SpriteRenderer(None)
    spriteRenderer.drawOrder = 50
    physicsComponent = PhysicsComponent()
    physicsComponent.mapToSpriteOnStart = False
    physicsComponent.friction = [10,10]
    physicsComponent.collidesWithLayers = [0]
    physicsComponent.bounds = [10,16]
    physicsComponent.offset = (0,6)
    physicsComponent.triggersWithLayers = [1]
    physicsComponent.physicsLayer = 1
    def OnTrigger(self : PhysicsComponent, other : PhysicsComponent):
        player = self.parentEntity.GetComponent(ActorComponent)
        if(player.heldItem == other.parentEntity):
            return

        if(other.parentEntity.GetComponent(ItemComponent)):

            if(player.heldItem):
                currentScene.DeleteEntity(player.heldItem)
                player.heldItem = None

            player.heldItem = other.parentEntity
    physicsComponent.onTriggerStart.append(OnTrigger)

    # Create dash after images
    for i in range(3):
        spriteRenderer = SpriteRenderer(None,40)
        playerComponent.afterImages.append(currentScene.CreateEntity("PlayerAfterImage",[0,0],components=[spriteRenderer]))

    return currentScene.CreateEntity("Player",[0,0],components=[actorComponent,spriteRenderer,physicsComponent, playerComponent])