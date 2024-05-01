import random

from engine.ecs import Entity
from engine.engine import Engine
from engine.systems import physics
from engine.systems.physics import PhysicsComponent
from engine.systems.renderer import SpriteRenderer, AnimatedSprite
from game import assets
from game.systems import playersystem
from game.systems.NPCSystem import NPCComponent

def CreatePlayer(scene):
    physicsComponent = physics.PhysicsComponent()
    physicsComponent.gravity = (0,250)
    physicsComponent.bounds = [10,16]
    physicsComponent.offset = (0,6)
    physicsComponent.mapToSpriteOnStart = False
    return scene.CreateEntity(name="Player",position=[0,0],components=[SpriteRenderer(None),playersystem.PlayerComponent(),physicsComponent])


def CreateSkeleton(scene,i):
    npcComponent = NPCComponent()

    npcComponent.idleAnim = AnimatedSprite([assets.dungeonTileSet["skelet_idle_anim_f0"],assets.dungeonTileSet["skelet_idle_anim_f1"],assets.dungeonTileSet["skelet_idle_anim_f2"],assets.dungeonTileSet["skelet_idle_anim_f3"]],6)
    npcComponent.runAnim = AnimatedSprite([assets.dungeonTileSet["skelet_run_anim_f0"],assets.dungeonTileSet["skelet_run_anim_f1"],assets.dungeonTileSet["skelet_run_anim_f2"],assets.dungeonTileSet["skelet_run_anim_f3"]],9)

    def SkeletonBehaviour(self : NPCComponent):
        if(self.speed > 0 and self.parentEntity.GetComponent(PhysicsComponent).IsTouchingDirection('right')):
            self.speed = -self.speed
        elif(self.speed < 0 and self.parentEntity.GetComponent(PhysicsComponent).IsTouchingDirection('left')):
            self.speed = -self.speed
        self.parentEntity.GetComponent(PhysicsComponent).Move((self.speed*Engine._instance.deltaTime,0))
        #print(self.parentEntity.GetComponent(PhysicsComponent).touchingDirections)

    npcComponent.behaviourTick = SkeletonBehaviour

    t = scene.CreateEntity("SkeletonEnemy",position=[i*16-100,0],components=[SpriteRenderer(npcComponent.idleAnim),npcComponent,physics.PhysicsComponent(gravity=(0,250))])
    t.GetComponent(PhysicsComponent).collidesWithLayers = [1]
    t.GetComponent(PhysicsComponent).physicsLayer = 1
    return t
