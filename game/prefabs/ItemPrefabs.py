from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.scenes.levelscene import LevelScene
from game import assets
from game.components.guncomponent import GunComponent
from game.components.projectilecomponent import ProjectileComponent


def SpawnProjectileFactory(gunComponent : GunComponent, spriteRenderer):
    def SpawnProjectile(currentScene: LevelScene):
        phys = PhysicsComponent()
        phys.physicsLayer = 1

        pSpriteRend = SpriteRenderer(gunComponent.projectileSprite, 100, False)
        pSpriteRend.sprite.SetRotation(spriteRenderer.sprite._rotation)
        pSpriteRend.sprite.SetScale((0.5, 0.5))

        projectile = ProjectileComponent(gunComponent.projectileSpeed,
                                         spriteRenderer.sprite._rotation-gunComponent.spriteRotationOffset,
                                         gunComponent.friendly)
        projectile.damage = gunComponent.damage

        currentScene.CreateEntity("Projectile",
                                  [int(gunComponent.parentEntity.position[0])
                                      , int(gunComponent.parentEntity.position[1])]
                                  , components=[pSpriteRend, phys,
                                                projectile])
    return SpawnProjectile

def CreateWoodenBowPrefab(currentScene : LevelScene, friendly=True):
    gunComponent = GunComponent()
    gunComponent.spriteRotationOffset = -45
    gunComponent.friendly = friendly
    gunComponent.projectileSprite = assets.itemTileset["flint_arrow"]
    spriteRenderer = SpriteRenderer(assets.itemTileset["wooden_bow"],60,False)
    spriteRenderer.sprite.SetScale((1,1))
    physics = PhysicsComponent()
    physics.collidesWithLayers = []
    physics.triggersWithLayers = []
    physics.physicsLayer = 1

    gunComponent.bulletPrefabFunc = SpawnProjectileFactory(gunComponent, spriteRenderer)

    return currentScene.CreateEntity("WoodenBow",[0,40],components=[gunComponent,spriteRenderer,physics])

def CreateSlingshotPrefab(currentScene : LevelScene, friendly=True):
    gunComponent = GunComponent()
    gunComponent.spriteRotationOffset = 60
    gunComponent.friendly = friendly
    gunComponent.projectileSprite = assets.itemTileset["stone_rock"]
    gunComponent.damage = 60
    gunComponent.projectileSpeed = 400
    spriteRenderer = SpriteRenderer(assets.itemTileset["slingshot"],60,False)
    spriteRenderer.sprite.SetScale((1,1))
    physics = PhysicsComponent()
    physics.collidesWithLayers = []
    physics.triggersWithLayers = []
    physics.physicsLayer = 1

    gunComponent.bulletPrefabFunc = SpawnProjectileFactory(gunComponent, spriteRenderer)

    return currentScene.CreateEntity("Slingshot",[0,40],components=[gunComponent,spriteRenderer,physics])