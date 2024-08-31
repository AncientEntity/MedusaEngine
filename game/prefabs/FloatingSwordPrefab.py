from engine.components.physicscomponent import PhysicsComponent
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


def CreateFloatingSwordPrefab(currentScene: LevelScene):
    actor = ActorComponent()
    actor.speed = 500
    actor.driver = FloatingSwordDriver()
    actor.meleeDamage = 25
    actor.meleeKnockbackForce = 250

    sprite = SpriteRenderer(assets.itemTileset["silver_sword"], 50, False)
    phys = PhysicsComponent()
    phys.mapToSpriteOnStart = False
    phys.bounds = [8, 8]
    phys.friction = [2,2]
    phys.collidesWithLayers = []
    phys.triggersWithLayers = [PHYSICS_PROJECTILES]
    phys.physicsLayer = PHYSICS_ENEMIES

    actor.driver.animations["idle"] = sprite.sprite
    actor.hitEffectSprites.append(actor.driver.animations["idle"])


    return currentScene.CreateEntity("Floating Sword Enemy", [0, 0], components=[actor, sprite, phys])