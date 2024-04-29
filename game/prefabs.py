import random

from engine.systems.renderer import SpriteRenderer, AnimatedSprite
from game import assets
from game.systems import playersystem
from game.systems.NPCSystem import NPCComponent

def CreatePlayer(scene):
    scene.CreateEntity("Player",position=[80,50],components=[SpriteRenderer(None),playersystem.PlayerComponent()])

def CreateSkeleton(scene):
    npcComponent = NPCComponent()

    npcComponent.idleAnim = AnimatedSprite([assets.dungeonTileSet["skelet_idle_anim_f0"],assets.dungeonTileSet["skelet_idle_anim_f1"],assets.dungeonTileSet["skelet_idle_anim_f2"],assets.dungeonTileSet["skelet_idle_anim_f3"]],6)
    npcComponent.runAnim = AnimatedSprite([assets.dungeonTileSet["skelet_run_anim_f0"],assets.dungeonTileSet["skelet_run_anim_f1"],assets.dungeonTileSet["skelet_run_anim_f2"],assets.dungeonTileSet["skelet_run_anim_f3"]],9)

    def SkeletonBehaviour(self):
        pass
    npcComponent.behaviourTick = SkeletonBehaviour

    scene.CreateEntity("SkeletonEnemy",position=[random.randint(-500,500),random.randint(-500,500)],components=[SpriteRenderer(npcComponent.idleAnim),npcComponent])
