from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.scenes.levelscene import LevelScene
from game import assets
from game.components.actorcomponent import ActorComponent
from game.drivers.testaidriver import TestAIDriver


def CreateGoblinPrefab(currentScene: LevelScene):
    actor = ActorComponent()
    actor.driver = TestAIDriver()
    actor.speed = 200

    sprite = SpriteRenderer(assets.dungeonTileSet["goblin_idle_anim_f0"], 50, False)
    phys = PhysicsComponent()
    phys.mapToSpriteOnStart = False
    phys.bounds = [8, 8]
    phys.friction = [10,10]

    return currentScene.CreateEntity("Gobin", [0, 0], components=[actor, sprite, phys])