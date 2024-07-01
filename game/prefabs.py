import random

from engine.components.rendering.particlecomponent import ParticleEmitterComponent, Particle
from engine.datatypes.sprites import AnimatedSprite
from engine.ecs import Entity
from engine.engine import Engine
from engine.systems import physics
from engine.systems.physics import PhysicsComponent
from engine.systems.renderer import SpriteRenderer
from game import assets
from game.systems import playersystem
from game.systems.NPCSystem import NPCComponent

def CreatePlayer(scene):
    physicsComponent = physics.PhysicsComponent()
    physicsComponent.gravity = (0,500)
    physicsComponent.bounds = [10,16]
    physicsComponent.offset = (0,6)
    physicsComponent.collidesWithLayers = [1]
    physicsComponent.triggersWithLayers = [0]
    physicsComponent.physicsLayer = 0
    physicsComponent.mapToSpriteOnStart = False
    def TriggersSomething(self,other):
        if(other.parentEntity.name == "SkeletonEnemy"):
            scene.DeleteEntity(other.parentEntity)
    physicsComponent.onTriggerStart.append(TriggersSomething)

    return scene.CreateEntity(name="Player",position=[0,0],components=[SpriteRenderer(None),playersystem.PlayerComponent(),physicsComponent])


def CreateSkeleton(scene):
    npcComponent = NPCComponent()

    npcComponent.idleAnim = AnimatedSprite([assets.dungeonTileSet["skelet_idle_anim_f0"],assets.dungeonTileSet["skelet_idle_anim_f1"],assets.dungeonTileSet["skelet_idle_anim_f2"],assets.dungeonTileSet["skelet_idle_anim_f3"]],6)
    npcComponent.runAnim = AnimatedSprite([assets.dungeonTileSet["skelet_run_anim_f0"],assets.dungeonTileSet["skelet_run_anim_f1"],assets.dungeonTileSet["skelet_run_anim_f2"],assets.dungeonTileSet["skelet_run_anim_f3"]],9)

    def SkeletonBehaviour(self : NPCComponent):
        if(self.speed > 0 and self.parentEntity.GetComponent(PhysicsComponent).IsTouchingDirection('right')):
            self.speed = -self.speed
        elif(self.speed < 0 and self.parentEntity.GetComponent(PhysicsComponent).IsTouchingDirection('left')):
            self.speed = -self.speed
        self.parentEntity.GetComponent(PhysicsComponent).Move((self.speed*Engine._instance.deltaTime,0))

    npcComponent.behaviourTick = SkeletonBehaviour

    t = scene.CreateEntity("SkeletonEnemy",position=[0,0],components=[SpriteRenderer(npcComponent.idleAnim),npcComponent,physics.PhysicsComponent(gravity=(0,250))])
    t.GetComponent(PhysicsComponent).collidesWithLayers = [1,2]
    t.GetComponent(PhysicsComponent).triggersWithLayers = [0,2]
    t.GetComponent(PhysicsComponent).physicsLayer = 0
    t.GetComponent(PhysicsComponent).mapToSpriteOnStart = False
    t.GetComponent(PhysicsComponent).bounds = [10,16]
    return t

def CreateParticleTestPrefab(scene):
    particleComponent = ParticleEmitterComponent()


    particleComponent.sprite.SetColor((random.randint(0,255),random.randint(0,255),random.randint(0,255)))

    return scene.CreateEntity("PARTICLE",[0,0],components=[particleComponent])