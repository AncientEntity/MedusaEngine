import pygame

from engine.ecs import Component, EntitySystem, Scene
from engine.logging import Log, LOG_WARNINGS
from engine.systems.renderer import SpriteRenderer


class PhysicsComponent(Component):
    def __init__(self,bounds=[10,10]):
        super().__init__()
        self.bounds = bounds #centered on parent entity's position
        self._moveRequest = None
        self.mapToSpriteOnStart = True
    def Move(self,movement ):
        if(self._moveRequest == None):
            self._moveRequest = [0,0]
        self._moveRequest[0] += movement[0]
        self._moveRequest[1] += movement[1]

    #Makes bounds the same as the sprite's width/height
    def MapToSpriteRenderer(self):
        sR : SpriteRenderer = self.parentEntity.GetComponent(SpriteRenderer)
        if(sR == None):
            Log("Sprite not found when map to sprite renderer. ",LOG_WARNINGS)
            return
        self.bounds = [sR.sprite.get_width(),sR.sprite.get_height()]

class PhysicsSystem(EntitySystem):
    def __init__(self):
        super().__init__([PhysicsComponent])
    def Update(self,currentScene : Scene):
        body : PhysicsComponent
        for body in currentScene.components[PhysicsComponent]:
            if(body._moveRequest == None):
                continue
            body.parentEntity.position[0] += body._moveRequest[0]
            body.parentEntity.position[1] += body._moveRequest[1]

            other : PhysicsComponent
            for other in currentScene.components[PhysicsComponent]:
                if(body == other):
                    continue

                bodyPos = body.parentEntity.position
                otherPos = other.parentEntity.position
                bodyBounds = pygame.Rect(bodyPos[0]-body.bounds[0]//2,bodyPos[1]-body.bounds[1]//2,body.bounds[0],body.bounds[1])
                otherBounds = pygame.Rect(otherPos[0]-other.bounds[0]//2,otherPos[1]-other.bounds[1]//2,other.bounds[0],other.bounds[1])

                pygame.draw.rect(self.game.display,(0,255,0),bodyBounds)
                pygame.draw.rect(self.game.display,(0,0,255),otherBounds)

                if(bodyBounds.colliderect(otherBounds)):
                    #body and other are colliding.
                    if (body._moveRequest[0] > 0 and bodyPos[0] < otherPos[0] and abs(bodyBounds.top - otherBounds.bottom) > 1 and abs(bodyBounds.bottom - otherBounds.top) > 1):
                        bodyPos[0] = otherBounds.left-bodyBounds.width//2
                    elif (body._moveRequest[0] < 0 and bodyPos[0] > otherPos[0] and abs(bodyBounds.top - otherBounds.bottom) > 1 and abs(bodyBounds.bottom - otherBounds.top) > 1):
                        bodyPos[0] = otherBounds.right+bodyBounds.width//2
                    if (body._moveRequest[1] > 0 and bodyPos[1] < otherPos[1] and abs(bodyBounds.left - otherBounds.right) > 1 and abs(bodyBounds.right - otherBounds.left) > 1):
                        bodyPos[1] = otherBounds.top-bodyBounds.height//2
                    elif (body._moveRequest[1] < 0 and bodyPos[1] > otherPos[1] and abs(bodyBounds.left - otherBounds.right) > 1 and abs(bodyBounds.right - otherBounds.left) > 1):
                        bodyPos[1] = otherBounds.bottom + bodyBounds.height // 2

            body._moveRequest = None

        pygame.display.update()

    def OnEnable(self):
        body : PhysicsComponent
        for body in self.game.GetCurrentScene().components[PhysicsComponent]:
            if(body.mapToSpriteOnStart):
                body.MapToSpriteRenderer()