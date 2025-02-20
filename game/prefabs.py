import random

from engine.components.rendering.particlecomponent import ParticleEmitterComponent, Particle
from engine.datatypes.sprites import AnimatedSprite
from engine.ecs import Entity, Scene
from engine.engine import Engine
from engine.systems import physics
from engine.systems.physics import PhysicsComponent
from engine.systems.renderer import SpriteRenderer
from game import assets
from game.systems import playersystem
from game.systems.NPCSystem import NPCComponent
from engine.datatypes import assetmanager

def CreatePlayer(entity : Entity, currentScene : Scene):
    entity.name = "Player"
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
            currentScene.DeleteEntity(other.parentEntity)
    physicsComponent.onTriggerStart.append(TriggersSomething)

    currentScene.AddComponents([SpriteRenderer(None),playersystem.PlayerComponent(),physicsComponent], entity)
    return entity

assetmanager.assets.prefabs['player'] = CreatePlayer

def CreateSkeleton(entity : Entity, currentScene : Scene):
    entity.name = "SkeletonEnemy"
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

    currentScene.AddComponents([SpriteRenderer(npcComponent.idleAnim),npcComponent,physics.PhysicsComponent(gravity=(0,250))], entity)
    entity.GetComponent(PhysicsComponent).collidesWithLayers = [1, 2]
    entity.GetComponent(PhysicsComponent).triggersWithLayers = [0, 2]
    entity.GetComponent(PhysicsComponent).physicsLayer = 0
    entity.GetComponent(PhysicsComponent).mapToSpriteOnStart = False
    entity.GetComponent(PhysicsComponent).bounds = [10, 16]
    return entity


assetmanager.assets.prefabs['skeleton'] = CreateSkeleton

def CreateParticleTestPrefab(entity : Entity, currentScene : Scene):
    entity.name = "Particle Test"
    particleComponent = ParticleEmitterComponent()


    particleComponent.sprite.SetColor((random.randint(0,255),random.randint(0,255),random.randint(0,255)))

    currentScene.AddComponents([particleComponent], entity)
    return entity

assetmanager.assets.prefabs['particletest'] = CreateParticleTestPrefab