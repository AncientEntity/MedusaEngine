from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.pathfinding import TilePathfinderHelper, TilemapPathfinder
from engine.datatypes.sprites import AnimatedSprite
from engine.scenes.levelscene import LevelScene
from game import assets
from game.components.actorcomponent import ActorComponent
from game.constants import PHYSICS_PLAYER, PHYSICS_ENEMIES, PHYSICS_PROJECTILES, PHYSICS_WALLS
from game.drivers.enemydriver import EnemyDriver
from game.prefabs.ItemPrefabs import CreateWoodenBowPrefab, CreateSlingshotPrefab


def CreateGoblinPrefab(currentScene: LevelScene):
    actor = ActorComponent()
    actor.speed = 400
    actor.driver = EnemyDriver()
    actor.heldItem = CreateSlingshotPrefab(currentScene, False)
    actor.heldItem.held = True

    actor.driver.pathfinder = TilePathfinderHelper(
        TilemapPathfinder(list(currentScene.tileMapLayersByName.values()),
                          [PHYSICS_WALLS]))

    sprite = SpriteRenderer(assets.dungeonTileSet["goblin_idle_anim_f0"], 50, False)
    phys = PhysicsComponent()
    phys.mapToSpriteOnStart = False
    phys.bounds = [8, 8]
    phys.friction = [10,10]
    phys.collidesWithLayers = [PHYSICS_WALLS, PHYSICS_ENEMIES]
    phys.triggersWithLayers = [PHYSICS_PROJECTILES]
    phys.physicsLayer = PHYSICS_ENEMIES

    actor.driver.animations["idle"] = AnimatedSprite(
        [assets.dungeonTileSet["goblin_idle_anim_f0"], assets.dungeonTileSet["goblin_idle_anim_f1"],
         assets.dungeonTileSet["goblin_idle_anim_f2"], assets.dungeonTileSet["goblin_idle_anim_f3"]], 5)
    actor.driver.animations["side"] = AnimatedSprite(
        [assets.dungeonTileSet["goblin_run_anim_f0"], assets.dungeonTileSet["goblin_run_anim_f1"],
         assets.dungeonTileSet["goblin_run_anim_f2"], assets.dungeonTileSet["goblin_run_anim_f3"]], 10)

    return currentScene.CreateEntity("Gobin", [0, 0], components=[actor, sprite, phys])