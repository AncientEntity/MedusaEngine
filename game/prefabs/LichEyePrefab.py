from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.particlecomponent import ParticleEmitterComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.pathfinding import TilePathfinderHelper, TilemapPathfinder
from engine.datatypes.sprites import AnimatedSprite
from engine.scenes.levelscene import LevelScene
from game import assets
from game.components.actorcomponent import ActorComponent
from game.components.itemcomponent import ItemComponent
from game.constants import PHYSICS_PLAYER, PHYSICS_ENEMIES, PHYSICS_PROJECTILES, PHYSICS_WALLS
from game.drivers.floatingsworddriver import FloatingSwordDriver
from game.drivers.walkingenemydriver import WalkingEnemyDriver
from game.prefabs.ItemPrefabs import CreateWoodenBowPrefab, CreateSlingshotPrefab
from pygame import Rect


def CreateLichEyePrefab(currentScene: LevelScene):
    actor = ActorComponent()
    actor.speed = 85
    actor.driver = WalkingEnemyDriver()
    actor.meleeDamage = 25
    actor.meleeKnockbackForce = 200

    actor.driver.pathfinder = TilePathfinderHelper(
        TilemapPathfinder(list(currentScene.tileMapLayersByName.values()),
                          [PHYSICS_WALLS]))

    sprite = SpriteRenderer(assets.lichEye["lich_regular"], 50, False)
    phys = PhysicsComponent()
    phys.mapToSpriteOnStart = False
    phys.bounds = [13, 13]
    phys.friction = [4,4]
    phys.collidesWithLayers = [PHYSICS_WALLS, PHYSICS_ENEMIES]
    phys.triggersWithLayers = [PHYSICS_PROJECTILES]
    phys.physicsLayer = PHYSICS_ENEMIES

    actor.driver.animations["idle"] = sprite.sprite
    actor.hitEffectSprites.append(actor.driver.animations["idle"])

    particles = ParticleEmitterComponent()
    particles.gravity = (0,500)
    particles.sprite.SetColor((255,50,50))
    particles.sprite.SetScale((0.25,0.25))
    particles.lifeTimeRange = (0.1,0.3)
    particles.spawnBounds = Rect(-5,0,5,6)
    particles.prewarm = True
    particles.particlesPerSecond = 75


    return currentScene.CreateEntity("Lich Eye Enemy", [0, 0], components=[actor, sprite, phys, particles])