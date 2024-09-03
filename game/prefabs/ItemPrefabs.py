from pygame import Rect

from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.particlecomponent import ParticleEmitterComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.sprites import Sprite
from engine.scenes.levelscene import LevelScene
from game import assets
from game.components.guncomponent import GunComponent
from game.components.projectilecomponent import ProjectileComponent
from game.constants import PHYSICS_OBJECTS, PHYSICS_PROJECTILES


def SpawnProjectileFactory(gunComponent : GunComponent, spriteRenderer, additionalComponentFactories=[]):
    def SpawnProjectile(currentScene: LevelScene):
        phys = PhysicsComponent()
        phys.physicsLayer = PHYSICS_PROJECTILES

        phys.collidesWithLayers = []
        phys.triggersWithLayers = []

        pSpriteRend = SpriteRenderer(gunComponent.projectileSprite, 100, False)
        pSpriteRend.sprite.SetRotation(spriteRenderer.sprite._rotation)
        pSpriteRend.sprite.SetScale((0.5, 0.5))

        projectile = ProjectileComponent(gunComponent.projectileSpeed,
                                         spriteRenderer.sprite._rotation-gunComponent.spriteRotationOffset,
                                         gunComponent.friendly)
        projectile.damage = gunComponent.damage
        projectile.owningActor = gunComponent.owningActor

        components = [pSpriteRend, phys, projectile]
        for componentFactory in additionalComponentFactories:
            components.append(componentFactory())

        currentScene.CreateEntity("Projectile",
                                  [int(gunComponent.parentEntity.position[0])
                                      , int(gunComponent.parentEntity.position[1])]
                                  , components=components)
    return SpawnProjectile

def CreateWoodenBowPrefab(currentScene : LevelScene, friendly=True):
    gunComponent = GunComponent()
    gunComponent.spriteRotationOffset = -45
    gunComponent.friendly = friendly
    gunComponent.damage = 80
    gunComponent.ammoPerMagazine = 5
    gunComponent.ammo = 5
    gunComponent.projectileSpeed = 150
    gunComponent.projectileSprite = assets.itemTileset["flint_arrow"]
    spriteRenderer = SpriteRenderer(assets.itemTileset["wooden_bow"],60,False)
    spriteRenderer.sprite.SetScale((1,1))
    physics = PhysicsComponent()
    physics.collidesWithLayers = []
    physics.triggersWithLayers = []
    physics.physicsLayer = PHYSICS_OBJECTS

    gunComponent.bulletPrefabFunc = SpawnProjectileFactory(gunComponent, spriteRenderer)

    return currentScene.CreateEntity("WoodenBow",[0,40],components=[gunComponent,spriteRenderer,physics])

def CreateSlingshotPrefab(currentScene : LevelScene, friendly=True):
    gunComponent = GunComponent()
    gunComponent.spriteRotationOffset = 60
    gunComponent.friendly = friendly
    gunComponent.projectileSprite = assets.itemTileset["stone_rock"]
    gunComponent.damage = 25
    gunComponent.ammoPerMagazine = 8
    gunComponent.ammo = 8
    gunComponent.projectileSpeed = 100
    gunComponent.spriteRotateHalf = True
    gunComponent.shootDelay = 0.65
    spriteRenderer = SpriteRenderer(assets.itemTileset["slingshot"],60,False)
    spriteRenderer.sprite.SetScale((1,1))
    physics = PhysicsComponent()
    physics.collidesWithLayers = []
    physics.triggersWithLayers = []
    physics.physicsLayer = PHYSICS_OBJECTS

    gunComponent.bulletPrefabFunc = SpawnProjectileFactory(gunComponent, spriteRenderer)

    return currentScene.CreateEntity("Slingshot",[0,40],components=[gunComponent,spriteRenderer,physics])

def CreateLichFireballPrefab(currentScene : LevelScene, friendly=False):
    def ParticleEmitterFactory():
        particles = ParticleEmitterComponent()
        particles.gravity = (0, 0)
        particles.sprite.SetColor((255, 50, 50))
        particles.sprite.SetScale((0.25, 0.25))
        particles.lifeTimeRange = (0.1, 0.3)
        particles.spawnBounds = Rect(-2, 0, 2, 2)
        particles.prewarm = True
        particles.particlesPerSecond = 75
        return particles

    gunComponent = GunComponent()
    gunComponent.spriteRotationOffset = 60
    gunComponent.friendly = friendly
    gunComponent.projectileSprite = Sprite(assets.itemTileset["stone_rock"])
    gunComponent.projectileSprite.SetAlpha(0)
    gunComponent.damage = 25
    gunComponent.ammoPerMagazine = 8
    gunComponent.ammo = 8
    gunComponent.projectileSpeed = 100
    gunComponent.spriteRotateHalf = True
    gunComponent.shootDelay = 0.8

    # Needs sprite renderer to track rotation, but enabled = False so it doesnt appear.
    spriteRenderer = SpriteRenderer(assets.itemTileset["slingshot"],60,False)
    spriteRenderer.sprite.SetScale((1,1))
    spriteRenderer.enabled = False

    physics = PhysicsComponent()
    physics.collidesWithLayers = []
    physics.triggersWithLayers = []
    physics.physicsLayer = PHYSICS_OBJECTS

    gunComponent.bulletPrefabFunc = SpawnProjectileFactory(gunComponent, spriteRenderer, [ParticleEmitterFactory])

    return currentScene.CreateEntity("Slingshot",[0,40],components=[gunComponent,spriteRenderer,physics])