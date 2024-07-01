from engine.components.rendering.particlecomponent import ParticleEmitterComponent
import pygame

def CreateJammedParticlesPrefab(currentScene, position):
    jammedParticles = ParticleEmitterComponent()
    jammedParticles.lifeTimeRange = [0.5, 1]
    jammedParticles.sprite.SetScale((0.5, 0.5))
    jammedParticles.sprite.SetTint((180, 10, 10))
    jammedParticles.spawnBounds = pygame.Rect(-4, -4, 4, 4)
    jammedParticles.drawOrder = 50
    return currentScene.CreateEntity("Jammed Particles", position, [jammedParticles])