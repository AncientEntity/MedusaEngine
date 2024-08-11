from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.scenes.levelscene import LevelScene
from game import assets
from game.components.monstercomponent import MonsterComponent


def CreateTestMonster(currentScene : LevelScene):
    monster = MonsterComponent()
    sprite = SpriteRenderer(assets.dungeonTileSet["goblin_idle_anim_f0"],50,False)
    phys = PhysicsComponent()
    phys.mapToSpriteOnStart = False
    phys.bounds = [8,8]


    return currentScene.CreateEntity("TestMonster",[0,0],components=[monster,sprite, phys])