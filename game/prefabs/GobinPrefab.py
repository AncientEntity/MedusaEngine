from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.datatypes.pathfinding import TilePathfinderHelper, TilemapPathfinder
from engine.datatypes.sprites import AnimatedSprite
from engine.scenes.levelscene import LevelScene
from game import assets
from game.components.actorcomponent import ActorComponent
from game.drivers.enemydriver import EnemyDriver
from game.prefabs.ItemPrefabs import CreateWoodenBowPrefab


def CreateGoblinPrefab(currentScene: LevelScene):
    actor = ActorComponent()
    actor.speed = 400
    actor.driver = EnemyDriver()
    actor.heldItem = CreateWoodenBowPrefab(currentScene, False)

    actor.driver.pathfinder = TilePathfinderHelper(
        TilemapPathfinder(list(currentScene.tileMapLayersByName.values()),
                          [0]))

    sprite = SpriteRenderer(assets.dungeonTileSet["goblin_idle_anim_f0"], 50, False)
    phys = PhysicsComponent()
    phys.mapToSpriteOnStart = False
    phys.bounds = [8, 8]
    phys.friction = [10,10]
    phys.triggersWithLayers = [1]

    actor.driver.animations["idle"] = AnimatedSprite(
        [assets.dungeonTileSet["goblin_idle_anim_f0"], assets.dungeonTileSet["goblin_idle_anim_f1"],
         assets.dungeonTileSet["goblin_idle_anim_f2"], assets.dungeonTileSet["goblin_idle_anim_f3"]], 5)
    actor.driver.animations["side"] = AnimatedSprite(
        [assets.dungeonTileSet["goblin_run_anim_f0"], assets.dungeonTileSet["goblin_run_anim_f1"],
         assets.dungeonTileSet["goblin_run_anim_f2"], assets.dungeonTileSet["goblin_run_anim_f3"]], 10)

    return currentScene.CreateEntity("Gobin", [0, 0], components=[actor, sprite, phys])