import pygame

from engine.components.physicscomponent import PhysicsComponent
from engine.datatypes.quadtree import QuadNode
from engine.ecs import Component, EntitySystem, Scene
from engine.logging import Log, LOG_INFO, LOG_WARNINGS
from engine.systems.renderer import TilemapRenderer
import math


class PhysicsSystem(EntitySystem):
    def __init__(self):
        super().__init__([PhysicsComponent])
        self.stepsPerFrame = 2

        self.quadtree : QuadNode = None
        self.rootQuadSize : tuple(int) = None

    def OnEnable(self, currentScene : Scene):
        self.rootQuadSize = (currentScene.sceneSize[0] / -2, currentScene.sceneSize[1] / -2,currentScene.sceneSize[1],currentScene.sceneSize[1])
        self.quadtree = QuadNode(None, pygame.Rect( *self.rootQuadSize))
        logCheck = (math.log(currentScene.sceneSize[0],2),math.log(currentScene.sceneSize[1],2))
        if logCheck[0] != int(logCheck[0]) or logCheck[1] != int(logCheck[1]):
            Log("QuadTree bounds are not a power of 2. May cause a division error, consider changing currentScene.sceneSize to a power of 2.", LOG_WARNINGS)
        Log(f"QuadTree initialized with size: {self.quadtree.bounds}", LOG_INFO)

    def Update(self,currentScene : Scene):
        for i in range(self.stepsPerFrame):
            self.Step(currentScene,self.game.deltaTime/self.stepsPerFrame)

    def Step(self, currentScene : Scene, stepTime):
        body : PhysicsComponent

        # Reset body step properties
        for body in currentScene.components[PhysicsComponent]:
            body.ResetCollisionDirections()
            body._lastStepTriggeredWith = body._thisStepTriggeredWith
            body._thisStepTriggeredWith = []

        # Rebuild quad tree (this is only temporary, the branch spatialpartitioning-optimized will instead
        # update objects based on if they have moved. But this is still faster.
        self.quadtree = QuadNode(None,self.quadtree.bounds)
        for body in currentScene.components[PhysicsComponent]:
            body._overlappingSpatialPartitions.clear()
            self.quadtree.AddBody(body)

        #Physics Component Collision
        for body in currentScene.components[PhysicsComponent]:
            if(body.static): #If static do not check for collisions with others, as it should be stationary.
                continue
            #Add gravity
            self.ApplyGravity(body,stepTime)

            #Add velocity movement
            if(body.velocity[0] != 0 or body.velocity[1] != 0):
                body.velocity[0] *= 1.0 - body.friction[0] * stepTime
                body.velocity[1] *= 1.0 - body.friction[1] * stepTime
                body.Move((body.velocity[0] * stepTime,body.velocity[1] * stepTime))

            #If we aren't moving the object then skip
            if(body._moveRequest == None):
                continue
            body.parentEntity.position[0] += body._moveRequest[0]
            body.parentEntity.position[1] += body._moveRequest[1]

            #Physics Component Collision
            other : PhysicsComponent
            for other in QuadNode.GetBodiesInSharedSpace(body):
                if(body == other or self.DoBodiesInteract(body,other) == False):
                    continue

                bodyPos = [body.parentEntity.position[0]+body.offset[0],body.parentEntity.position[1]+body.offset[1]]
                otherPos = other.parentEntity.position # todo investigate, i believe we should be adding other.offset here
                bodyBounds = pygame.FRect(bodyPos[0]-body.bounds[0]/2,bodyPos[1]-body.bounds[1]/2,body.bounds[0],body.bounds[1])
                otherBounds = pygame.FRect(otherPos[0]-other.bounds[0]/2,otherPos[1]-other.bounds[1]/2,other.bounds[0],other.bounds[1])
                self.HandlePhysicsCollision(body,bodyPos,bodyBounds,other,otherBounds.center,otherBounds,False)

            #Tileset Collision
            for tilemapRenderer in currentScene.components[TilemapRenderer]:
                if(tilemapRenderer.tileMap == None or (tilemapRenderer.physicsLayer not in body.collidesWithLayers and tilemapRenderer.physicsLayer not in body.triggersWithLayers)):
                    continue

                bodyPos = [body.parentEntity.position[0]+body.offset[0],body.parentEntity.position[1]+body.offset[1]]
                bodyBounds = pygame.FRect(bodyPos[0]-body.bounds[0]/2,bodyPos[1]-body.bounds[1]/2,body.bounds[0],body.bounds[1])

                topLeftOverlap = tilemapRenderer.WorldPositionToTileIndex(((int(bodyBounds.left),int(bodyBounds.top))))
                bottomRightOverlap = tilemapRenderer.WorldPositionToTileIndex(((int(bodyBounds.right),int(bodyBounds.bottom))))
                overlappingTiles = tilemapRenderer.GetOverlappingTilesInWorldSpace(topLeftOverlap, bottomRightOverlap)
                for tile in overlappingTiles: #Only check overlapping tiles.
                    if(False == tilemapRenderer.tileMap.tileSet[tile[0]].ignoreCollision):
                        otherBounds = pygame.FRect(tile[1][0], tile[1][1], tilemapRenderer.tileMap.tileSize, tilemapRenderer.tileMap.tileSize)
                        self.HandlePhysicsCollision(body,bodyPos,bodyBounds,None,otherBounds.center,otherBounds,tilemapRenderer.physicsLayer not in body.collidesWithLayers)

            body._moveRequest = None

    def OnNewComponent(self,component : Component):
        if (type(component) == PhysicsComponent and component.mapToSpriteOnStart):
            component.MapToSpriteRenderer()

    def HandlePhysicsCollision(self,body : PhysicsComponent,bodyPos,bodyBounds : pygame.FRect,other : PhysicsComponent,otherPos,otherBounds : pygame.FRect,onlyTrigger):

        bodyAndOtherCollides = (other == None or other.physicsLayer in body.collidesWithLayers) and False == onlyTrigger

        #If colliding handle accordingly, otherwise we have an else statement below that detects touching.
        if (bodyBounds.colliderect(otherBounds)):
            # body and other are colliding.

            #Handle Triggering
            self.HandleTriggerPhysics(body,other)

            if(bodyAndOtherCollides):

                # Right
                if (body._moveRequest[0] > 0 and bodyPos[0] < otherPos[0] and abs(
                        bodyBounds.top - otherBounds.bottom) > 1 and abs(bodyBounds.bottom - otherBounds.top) > 1):
                    bodyBounds.right = otherBounds.left

                    body.touchingDirections['right'] = True
                    body.parentEntity.position[0] = bodyBounds.centerx - body.offset[0]
                    if(other != None and other.static == False and body.velocity[1] != 0):
                        other.touchingDirections['left'] = True

                        finalVelocity = (body.mass * body.velocity[0] + other.mass * other.velocity[0]) / (
                                    body.mass + other.mass)
                        body.velocity[0] = finalVelocity
                        other.velocity[0] = finalVelocity
                    else:
                        body.velocity[0] = 0

                # Left
                elif (body._moveRequest[0] < 0 and bodyPos[0] > otherPos[0] and abs(
                        bodyBounds.top - otherBounds.bottom) > 1 and abs(bodyBounds.bottom - otherBounds.top) > 1):
                    bodyBounds.left = otherBounds.right

                    body.touchingDirections['left'] = True
                    body.parentEntity.position[0] = bodyBounds.centerx - body.offset[0]
                    if(other != None and other.static == False and body.velocity[1] != 0):
                        other.touchingDirections['right'] = True

                        finalVelocity = (body.mass * body.velocity[0] + other.mass * other.velocity[0]) / (
                                    body.mass + other.mass)
                        body.velocity[0] = finalVelocity
                        other.velocity[0] = finalVelocity
                    else:
                        body.velocity[0] = 0

                # Bottom
                if (body._moveRequest[1] > 0 and bodyPos[1] < otherPos[1] and abs(
                        bodyBounds.left - otherBounds.right) > 1 and abs(bodyBounds.right - otherBounds.left) > 1):
                    bodyBounds.bottom = otherBounds.top

                    body.touchingDirections['bottom'] = True
                    body.parentEntity.position[1] = bodyBounds.centery - body.offset[1]
                    if(other != None and other.static == False and body.velocity[1] != 0):
                        other.touchingDirections['top'] = True

                        finalVelocity = (body.mass * body.velocity[1] + other.mass * other.velocity[1]) / (
                                    body.mass + other.mass)
                        body.velocity[1] = finalVelocity
                        other.velocity[1] = finalVelocity
                    else:
                        body.velocity[1] = 0

                # Top
                elif (body._moveRequest[1] < 0 and bodyPos[1] > otherPos[1] and abs(
                        bodyBounds.left - otherBounds.right) > 1 and abs(bodyBounds.right - otherBounds.left) > 1):
                    bodyBounds.top = otherBounds.bottom

                    body.touchingDirections['top'] = True
                    body.parentEntity.position[1] = bodyBounds.centery - body.offset[1]
                    if(other != None and other.static == False and body.velocity[1] != 0):
                        other.touchingDirections['bottom'] = True

                        finalVelocity = (body.mass * body.velocity[1] + other.mass * other.velocity[1]) / (
                                    body.mass + other.mass)
                        body.velocity[1] = finalVelocity
                        other.velocity[1] = finalVelocity
                    else:
                        body.velocity[1] = 0

        else:
            if (bodyBounds.left == otherBounds.right and round(bodyBounds.bottom) >= round(otherBounds.bottom) and round(bodyBounds.top) <= round(otherBounds.top)):
                body.touchingDirections['left'] = True
                if(other != None):
                    other.touchingDirections['right'] = True
                    self.HandleTriggerPhysics(body, other)
            if (bodyBounds.right == otherBounds.left and round(bodyBounds.bottom) >= round(otherBounds.bottom) and round(bodyBounds.top) <= round(otherBounds.top)):
                body.touchingDirections['right'] = True
                if(other != None):
                    other.touchingDirections['left'] = True
                    self.HandleTriggerPhysics(body, other)
            if (bodyBounds.top == otherBounds.bottom and round(bodyBounds.right) >= round(otherBounds.left) and round(bodyBounds.left) <= round(otherBounds.right)):
                body.touchingDirections['top'] = True
                if(other != None):
                    other.touchingDirections['bottom'] = True
                    self.HandleTriggerPhysics(body, other)
            if (bodyBounds.bottom == otherBounds.top and round(bodyBounds.right) >= round(otherBounds.left) and round(bodyBounds.left) <= round(otherBounds.right)):
                body.touchingDirections['bottom'] = True
                if(other != None):
                    other.touchingDirections['top'] = True
                    self.HandleTriggerPhysics(body, other)
    def ApplyGravity(self,body,stepTime):
        if (body.gravity != None):
            body.velocity[0] += body.gravity[0] * stepTime
            body.velocity[1] += body.gravity[1] * stepTime

    def HandleTriggerPhysics(self,body,other):
        if (other != None):  # since we move body out of the way other will never detect it as a trigger. So we need them to both trigger.
            if (other.physicsLayer in body.triggersWithLayers):
                self.CheckTriggerStart(body, other)
            if (body.physicsLayer in other.triggersWithLayers):
                self.CheckTriggerStart(other, body)

    def CheckTriggerStart(self,body1,body2):
        if (body2 not in body1._lastStepTriggeredWith and body2 not in body1._thisStepTriggeredWith):
            for triggerStartFunc in body1.onTriggerStart:
                triggerStartFunc(body1, body2)
        body1._thisStepTriggeredWith.append(body2)

    def DoBodiesInteract(self,body1 : PhysicsComponent,body2 : PhysicsComponent):
        return body1.physicsLayer in body2.collidesWithLayers or body1.physicsLayer in body2.triggersWithLayers or body2.physicsLayer in body1.collidesWithLayers or body2.physicsLayer in body1.triggersWithLayers

    def DebugDrawQuads(self,renderer, quad : QuadNode):
        if(quad == None):
            return
        if(quad.bounds.w <= 1024):
            renderer.DebugDrawWorldRect((255,0,0),quad.bounds)
        for c in quad._quadrantChildren:
            self.DebugDrawQuads(renderer,c)

    def DebugDrawCollisionBounds(self, renderer, currentScene : Scene):
        physics : PhysicsComponent
        for body in currentScene.components[PhysicsComponent]:
            bodyPos = [body.parentEntity.position[0] + body.offset[0], body.parentEntity.position[1] + body.offset[1]]
            bodyBounds = pygame.FRect(bodyPos[0] - body.bounds[0] / 2, bodyPos[1] - body.bounds[1] / 2, body.bounds[0],
                                      body.bounds[1])

            renderer.DebugDrawWorldRect((0,255,0), bodyBounds)