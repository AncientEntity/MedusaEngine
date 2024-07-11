from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.scenes.levelscene import LevelScene
from game.components.playercomponent import PlayerComponent


def CreatePlayer(currentScene : LevelScene):
    playerComponent = PlayerComponent()
    spriteRenderer = SpriteRenderer(None)
    physicsComponent = PhysicsComponent()
    physicsComponent.mapToSpriteOnStart = False
    physicsComponent.friction = [10,10]
    physicsComponent.collidesWithLayers = []


    return currentScene.CreateEntity("Player",[0,0],components=[playerComponent,spriteRenderer,physicsComponent])