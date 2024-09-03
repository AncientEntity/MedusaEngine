from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.sprites import AnimatedSprite
from engine.scenes.levelscene import LevelScene
from game import assets
from game.components.actorcomponent import ActorComponent
from game.components.guncomponent import GunComponent
from game.components.itemcomponent import ItemComponent
from game.components.playercomponent import PlayerComponent
from game.constants import PHYSICS_PLAYER, PHYSICS_ENEMIES, PHYSICS_WALLS, PHYSICS_OBJECTS, PHYSICS_PROJECTILES
from game.drivers.playerdriver import PlayerDriver
from game.prefabs.ui.UIDashPrefab import UIDashPrefab
from game.prefabs.ui.UIHealthPrefab import UIHealthPrefabHandler


def CreatePlayer(currentScene : LevelScene):

    actorComponent : ActorComponent = ActorComponent()
    actorComponent.driver = PlayerDriver()
    actorComponent.friendly = True
    actorComponent.health = 200
    actorComponent.maxHealth = 200
    actorComponent.meleeDamage = 0

    playerComponent = PlayerComponent()
    playerComponent.dashUI = UIDashPrefab(playerComponent, actorComponent)

    actorComponent.hitEffectSprites.append(playerComponent.idleAnim)
    actorComponent.hitEffectSprites.append(playerComponent.runAnim)

    spriteRenderer = SpriteRenderer(None)
    spriteRenderer.drawOrder = 50
    physicsComponent = PhysicsComponent()
    physicsComponent.mapToSpriteOnStart = False
    physicsComponent.friction = [10,10]
    physicsComponent.collidesWithLayers = [PHYSICS_WALLS]
    physicsComponent.bounds = [10,16]
    physicsComponent.offset = (0,6)
    physicsComponent.triggersWithLayers = [PHYSICS_ENEMIES, PHYSICS_OBJECTS, PHYSICS_PROJECTILES]
    physicsComponent.physicsLayer = PHYSICS_PLAYER
    def OnTrigger(self : PhysicsComponent, other : PhysicsComponent):
        player = self.parentEntity.GetComponent(ActorComponent)
        if(player.heldItem == other.parentEntity):
            return

        itemComp = other.parentEntity.GetComponent(ItemComponent)
        if(itemComp and itemComp.held == False):
            if(player.heldItem):
                currentScene.DeleteEntity(player.heldItem)
                currentGun = player.heldItem.GetComponent(GunComponent)
                if currentGun:
                    currentGun.uiAmmoPrefabHandler.Delete(currentScene)
                player.heldItem = None

            player.heldItem = other.parentEntity
            itemComp.held = True

            gunComp : GunComponent = other.parentEntity.GetComponent(GunComponent)
            if(gunComp):
                gunComp.friendly = True

    physicsComponent.onTriggerStart.append(OnTrigger)

    # Create dash after images
    for i in range(3):
        afterSpriteRenderer = SpriteRenderer(None,40)
        playerComponent.afterImages.append(currentScene.CreateEntity("PlayerAfterImage",[0,0],components=[afterSpriteRenderer]))

    return currentScene.CreateEntity("Player",[0,0],components=[actorComponent,spriteRenderer,physicsComponent, playerComponent])