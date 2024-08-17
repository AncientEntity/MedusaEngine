from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.scenes.levelscene import LevelScene
from game import assets
from game.components.guncomponent import GunComponent
from game.components.projectilecomponent import ProjectileComponent


def SpawnProjectileFactory(gunComponent : GunComponent, spriteRenderer, friendly):
    def SpawnProjectile(currentScene: LevelScene):
        for i in range(10):

            pSpriteRend = SpriteRenderer(assets.worldTileset[0], 100, False)
            pSpriteRend.sprite.SetScale((0.25, 0.25))
            currentScene.CreateEntity("Projectile",
                                      [int(gunComponent.parentEntity.position[0])
                                          , int(gunComponent.parentEntity.position[1])]
                                      , components=[pSpriteRend,
                                                    ProjectileComponent(100, spriteRenderer.sprite._rotation+i*(360/10), friendly)])
    return SpawnProjectile

def CreatePistolPrefab(currentScene : LevelScene):
    gunComponent = GunComponent()
    spriteRenderer = SpriteRenderer(assets.worldTileset[0],60,False)
    spriteRenderer.sprite.SetScale((0.5,0.5))
    physics = PhysicsComponent()
    physics.collidesWithLayers = []
    physics.triggersWithLayers = []
    physics.physicsLayer = 1


    gunComponent.bulletPrefabFunc = SpawnProjectileFactory(gunComponent, spriteRenderer, True)

    return currentScene.CreateEntity("Gun",[0,40],components=[gunComponent,spriteRenderer,physics])