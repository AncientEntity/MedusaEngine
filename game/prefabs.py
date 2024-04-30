import random

from engine.systems import physics
from engine.systems.renderer import SpriteRenderer, AnimatedSprite
from game import assets
from game.systems import playersystem
from game.systems.NPCSystem import NPCComponent

def CreatePlayer(scene):
    physicsComponent = physics.PhysicsComponent()
    physicsComponent.gravity = (0,250)
    scene.CreateEntity(name="Player",position=[80,50],components=[SpriteRenderer(None),playersystem.PlayerComponent(),physicsComponent])

def CreateSkeleton(scene,i):
    npcComponent = NPCComponent()

    npcComponent.idleAnim = AnimatedSprite([assets.dungeonTileSet["skelet_idle_anim_f0"],assets.dungeonTileSet["skelet_idle_anim_f1"],assets.dungeonTileSet["skelet_idle_anim_f2"],assets.dungeonTileSet["skelet_idle_anim_f3"]],6)
    npcComponent.runAnim = AnimatedSprite([assets.dungeonTileSet["skelet_run_anim_f0"],assets.dungeonTileSet["skelet_run_anim_f1"],assets.dungeonTileSet["skelet_run_anim_f2"],assets.dungeonTileSet["skelet_run_anim_f3"]],9)

    def SkeletonBehaviour(self):
        pass
    npcComponent.behaviourTick = SkeletonBehaviour

    scene.CreateEntity("SkeletonEnemy",position=[i*16-160,200],components=[SpriteRenderer(npcComponent.idleAnim),npcComponent,physics.PhysicsComponent()])
