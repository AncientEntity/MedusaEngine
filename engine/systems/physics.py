import time

import pygame

from engine.ecs import Component, EntitySystem, Scene
from engine.logging import Log, LOG_WARNINGS
from engine.systems.renderer import SpriteRenderer, TilemapRenderer


class PhysicsComponent(Component):
    def __init__(self,bounds=[10,10],gravity=(0,0)):
        super().__init__()
        self.bounds = bounds #centered on parent entity's position
        self.offset = (0,0)
        self._moveRequest = None
        self.mapToSpriteOnStart = True
        self.touchingDirections = {'top':  False, 'bottom' : False, 'left' : False, 'right' : False}

        self.mass = 1.0

        self.static = False #If static it wont be checked in the physics loop as the main body only as other body.
        self.gravity : tuple(float) = gravity #either None or a tuple like: (0,9.84)
        self.velocity = [0,0]

    def Move(self,movement):
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

    def ResetCollisionDirections(self):
        self.touchingDirections['left'] = False
        self.touchingDirections['right'] = False
        self.touchingDirections['top'] = False
        self.touchingDirections['bottom'] = False

    def IsTouchingDirection(self,direction):
        if(direction == 'down'):
            direction = 'bottom'
        elif(direction == 'up'):
            direction = 'top'
        return self.touchingDirections[direction]

class PhysicsSystem(EntitySystem):
    def __init__(self):
        super().__init__([PhysicsComponent])
        self.stepsPerFrame = 2

    def Update(self,currentScene : Scene):
        for i in range(self.stepsPerFrame):
            self.Step(currentScene,self.game.deltaTime/self.stepsPerFrame)

    def Step(self, currentScene : Scene, stepTime):
        body : PhysicsComponent

        for body in currentScene.components[PhysicsComponent]:
            body.ResetCollisionDirections()

        #Physics Component Collision
        for body in currentScene.components[PhysicsComponent]:
            if(body.static): #If static do not check for collisions with others, as it should be stationary.
                continue

            #Add gravity
            self.ApplyGravity(body,stepTime)

            #Add velocity movement
            if(body.velocity[0] != 0 or body.velocity[1] != 0):
                body.Move((body.velocity[0] * stepTime,body.velocity[1] * stepTime))

            #If we aren't moving the object then skip
            if(body._moveRequest == None):
                continue
            body.parentEntity.position[0] += body._moveRequest[0]
            body.parentEntity.position[1] += body._moveRequest[1]


            #Physics Component Collision
            other : PhysicsComponent
            for other in currentScene.components[PhysicsComponent]:
                if(body == other):
                    continue

                bodyPos = [body.parentEntity.position[0]+body.offset[0],body.parentEntity.position[1]+body.offset[1]]
                otherPos = other.parentEntity.position
                bodyBounds = pygame.Rect(bodyPos[0]-body.bounds[0]//2,bodyPos[1]-body.bounds[1]//2,body.bounds[0],body.bounds[1])
                otherBounds = pygame.Rect(otherPos[0]-other.bounds[0]//2,otherPos[1]-other.bounds[1]//2,other.bounds[0],other.bounds[1])
                self.HandlePhysicsCollision(body,bodyPos,bodyBounds,other,otherBounds.center,otherBounds)

            #Tileset Collision
            for tilemapRenderer in currentScene.components[TilemapRenderer]:
                if(tilemapRenderer.tileMap == None):
                    continue

                bodyPos = [body.parentEntity.position[0]+body.offset[0],body.parentEntity.position[1]+body.offset[1]]
                bodyBounds = pygame.Rect(bodyPos[0]-body.bounds[0]//2,bodyPos[1]-body.bounds[1]//2,body.bounds[0],body.bounds[1])
                topLeftOverlap = tilemapRenderer.WorldToTilePosition((bodyBounds.left,bodyBounds.top))
                bottomRightOverlap = tilemapRenderer.WorldToTilePosition((bodyBounds.right,bodyBounds.bottom))
                overlappingTiles = tilemapRenderer.GetOverlappingTilesInTileSpace(topLeftOverlap,bottomRightOverlap)

                for tile in overlappingTiles: #Only check overlapping tiles.
                    if(tile[0] == -1):
                        continue
                    if(tilemapRenderer.tileMap.tileSet[tile[0]].hasCollision):
                        otherBounds = pygame.Rect(tile[1][0], tile[1][1], tilemapRenderer.tileMap.tileSize, tilemapRenderer.tileMap.tileSize)
                        self.HandlePhysicsCollision(body,bodyPos,bodyBounds,None,otherBounds.center,otherBounds)

            body._moveRequest = None

        pygame.display.update()

    def OnEnable(self):
        body : PhysicsComponent
        for body in self.game.GetCurrentScene().components[PhysicsComponent]:
            if(body.mapToSpriteOnStart):
                body.MapToSpriteRenderer()

    def HandlePhysicsCollision(self,body : PhysicsComponent,bodyPos,bodyBounds,other : PhysicsComponent,otherPos,otherBounds):
        #If colliding handle accordingly, otherwise we have an else statement below that detects touching.
        if (bodyBounds.colliderect(otherBounds)):
            # body and other are colliding.

            # Right
            if (body._moveRequest[0] > 0 and bodyPos[0] < otherPos[0] and abs(
                    bodyBounds.top - otherBounds.bottom) > 1 and abs(bodyBounds.bottom - otherBounds.top) > 1):
                bodyBounds.right = otherBounds.left #+1 so they are touching not colliding
                body.parentEntity.position[0] = bodyBounds.centerx-body.offset[0]
                body.velocity[0] = 0
                body.touchingDirections['right'] = True
                if(other != None):
                    other.touchingDirections['left'] = True
            # Left
            elif (body._moveRequest[0] < 0 and bodyPos[0] > otherPos[0] and abs(
                    bodyBounds.top - otherBounds.bottom) > 1 and abs(bodyBounds.bottom - otherBounds.top) > 1):
                bodyBounds.left = otherBounds.right #-1 so they are touching not colliding
                body.parentEntity.position[0] = bodyBounds.centerx-body.offset[0]
                body.velocity[0] = 0
                body.touchingDirections['left'] = True
                if(other != None):
                    other.touchingDirections['left'] = True

            # Bottom
            if (body._moveRequest[1] > 0 and bodyPos[1] < otherPos[1] and abs(
                    bodyBounds.left - otherBounds.right) > 1 and abs(bodyBounds.right - otherBounds.left) > 1):
                bodyBounds.bottom = otherBounds.top
                body.parentEntity.position[1] = bodyBounds.centery-body.offset[1]
                body.velocity[1] = 0

                body.touchingDirections['bottom'] = True
                if(other != None):
                    other.touchingDirections['top'] = True
            # Top
            elif (body._moveRequest[1] < 0 and bodyPos[1] > otherPos[1] and abs(
                    bodyBounds.left - otherBounds.right) > 1 and abs(bodyBounds.right - otherBounds.left) > 1):
                bodyBounds.top = otherBounds.bottom
                body.parentEntity.position[1] = bodyBounds.centery-body.offset[1]
                body.velocity[1] = 0

                body.touchingDirections['top'] = True
                if(other != None):
                    other.touchingDirections['bottom'] = True
        else:
            if (bodyBounds.left == otherBounds.right and bodyBounds.bottom >= otherBounds.bottom and bodyBounds.top <= otherBounds.top):
                body.touchingDirections['left'] = True
                if(other != None):
                    other.touchingDirections['right'] = True
            if (bodyBounds.right == otherBounds.left and bodyBounds.bottom >= otherBounds.bottom and bodyBounds.top <= otherBounds.top):
                body.touchingDirections['right'] = True
                if(other != None):
                    other.touchingDirections['left'] = True
            if (bodyBounds.top == otherBounds.bottom and bodyBounds.right >= otherBounds.left and bodyBounds.left <= otherBounds.right):
                body.touchingDirections['top'] = True
                if(other != None):
                    other.touchingDirections['bottom'] = True
            if (bodyBounds.bottom == otherBounds.top and bodyBounds.right >= otherBounds.left and bodyBounds.left <= otherBounds.right):
                body.touchingDirections['bottom'] = True
                if(other != None):
                    other.touchingDirections['top'] = True
    def ApplyGravity(self,body,stepTime):
        if (body.gravity != None):
            body.velocity[0] += body.gravity[0] * stepTime
            body.velocity[1] += body.gravity[1] * stepTime