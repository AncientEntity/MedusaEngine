import random

import pygame

from engine.components.rendering.renderercomponent import RendererComponent
from engine.datatypes.sprites import Sprite, GetSprite
import time

defaultParticle = Sprite(pygame.image.load("engine/art/default-particle.png"))

class Particle:
    def __init__(self):
        self.sprite = None
        self.position = [0,0]
        self.velocity = [0,0]
        self.gravity = [0,0]
        self.lifeTime = 5

#todo implement particle system :) it will still need to be added to RendererSystem's target components.
class ParticleEmitterComponent(RendererComponent):
    def __init__(self):
        super().__init__()
        self.sprite : Sprite = defaultParticle
        self.particlesPerSecond = 25.0
        self.maxParticles = 100
        self.particleInitializeFunction = None #Function that runs, takes argument particle : Particle. Meant to initialize particle.
        self.prewarm = False
        self._color = (255,255,255)
        self._lifeTimeRange = [0.1,5]
        self.gravity = [0,-35]
        self.spawnBounds = pygame.Rect(-10,-10,10,10)

        self._lastParticleSpawnTime = time.time()
        self._activeParticles = []

        self.SetSpriteColor(self._color)

    def SetSpriteColor(self,color):
        self._color = color
        newSprite = GetSprite(self.sprite).copy()
        newSprite.fill((0,0,0,255),None,pygame.BLEND_RGBA_MULT)
        newSprite.fill(self._color+(0,),None,pygame.BLEND_RGBA_ADD)
        self.sprite = newSprite

    def NewParticle(self):
        newParticle = Particle()
        newParticle.position = [self.parentEntity.position[0]+random.randint(self.spawnBounds.x,self.spawnBounds.w),self.parentEntity.position[1]+random.randint(self.spawnBounds.y,self.spawnBounds.h)]
        newParticle.sprite = self.sprite
        newParticle.lifeTime = random.uniform(self._lifeTimeRange[0],self._lifeTimeRange[1])
        newParticle.gravity = self.gravity
        if(self.particleInitializeFunction != None):
            self.particleInitializeFunction(newParticle)
        self._activeParticles.append(newParticle)