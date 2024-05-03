import pygame

from engine.ecs import Component, EntitySystem, Scene
from engine.logging import Log, LOG_WARNINGS
from engine.systems.renderer import SpriteRenderer, TilemapRenderer


class PhysicsComponent(Component):
    def __init__(self,bounds=[10,10],gravity=(0,0)):
        super().__init__()
        self.bounds = bounds #centered on parent entity's position
        self.offset = (0,0)
        self.mapToSpriteOnStart = True
        self.touchingDirections = {'top':  False, 'bottom' : False, 'left' : False, 'right' : False}

        self.physicsLayer = 0
        self.collidesWithLayers = [0]
        self.triggersWithLayers = [0]
        self.onTriggerStart = [] #List of functions that take in body : PhysicsComponent, other : PhysicsComponent. Runs when something 'first starts to trigger with self'

        self.friction = [5,0]
        self.mass = 1.0
        self.static = False #If static it wont be checked in the physics loop as the main body only as other body.
        self.gravity : tuple(float) = gravity #either None or a tuple like: (0,9.84)
        self.velocity = [0,0]

        self._moveRequest = None #Move() adds to this so the physics calculations know what the object wants.
        self._thisStepTriggeredWith = [] #List of other physics components that this collided with this frame.
        self._lastStepTriggeredWith = [] #List of other physics components that this collided with last frame.

    def Move(self,movement):
        if(self._moveRequest == None):
            self._moveRequest = [0,0]
        self._moveRequest[0] += movement[0]
        self._moveRequest[1] += movement[1]

    def AddVelocity(self,impulse):
        self.velocity[0] += impulse[0]
        self.velocity[1] += impulse[1]

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
            body._lastStepTriggeredWith = body._thisStepTriggeredWith
            body._thisStepTriggeredWith = []

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
            for other in currentScene.components[PhysicsComponent]:
                if(body == other or self.DoBodiesInteract(body,other) == False):
                    continue

                bodyPos = [body.parentEntity.position[0]+body.offset[0],body.parentEntity.position[1]+body.offset[1]]
                otherPos = other.parentEntity.position
                bodyBounds = pygame.FRect(bodyPos[0]-body.bounds[0]/2,bodyPos[1]-body.bounds[1]/2,body.bounds[0],body.bounds[1])
                otherBounds = pygame.FRect(otherPos[0]-other.bounds[0]/2,otherPos[1]-other.bounds[1]/2,other.bounds[0],other.bounds[1])
                self.HandlePhysicsCollision(body,bodyPos,bodyBounds,other,otherBounds.center,otherBounds,False)

            #Tileset Collision
            for tilemapRenderer in currentScene.components[TilemapRenderer]:
                if(tilemapRenderer.tileMap == None or (tilemapRenderer.physicsLayer not in body.collidesWithLayers and tilemapRenderer.physicsLayer not in body.triggersWithLayers)):
                    continue

                bodyPos = [body.parentEntity.position[0]+body.offset[0],body.parentEntity.position[1]+body.offset[1]]
                bodyBounds = pygame.FRect(bodyPos[0]-body.bounds[0]/2,bodyPos[1]-body.bounds[1]/2,body.bounds[0],body.bounds[1])

                topLeftOverlap = tilemapRenderer.WorldToTilePosition((int(bodyBounds.left),int(bodyBounds.top)))
                bottomRightOverlap = tilemapRenderer.WorldToTilePosition((int(bodyBounds.right),int(bodyBounds.bottom)))
                overlappingTiles = tilemapRenderer.GetOverlappingTilesInTileSpace(topLeftOverlap,bottomRightOverlap)
                for tile in overlappingTiles: #Only check overlapping tiles.
                    if(tile[0] == -1):
                        continue
                    if(False == tilemapRenderer.tileMap.tileSet[tile[0]].ignoreCollision):
                        otherBounds = pygame.FRect(tile[1][0], tile[1][1], tilemapRenderer.tileMap.tileSize, tilemapRenderer.tileMap.tileSize)
                        self.HandlePhysicsCollision(body,bodyPos,bodyBounds,None,otherBounds.center,otherBounds,tilemapRenderer.physicsLayer not in body.collidesWithLayers)

            body._moveRequest = None

        pygame.display.update()

    def OnEnable(self):
        body : PhysicsComponent
        for body in self.game.GetCurrentScene().components[PhysicsComponent]:
            if(body.mapToSpriteOnStart):
                body.MapToSpriteRenderer()

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
                    body.velocity[0] = 0
                    body.parentEntity.position[0] = bodyBounds.centerx - body.offset[0]

                    body.touchingDirections['right'] = True
                    if(other != None):
                        other.touchingDirections['left'] = True
                # Left
                elif (body._moveRequest[0] < 0 and bodyPos[0] > otherPos[0] and abs(
                        bodyBounds.top - otherBounds.bottom) > 1 and abs(bodyBounds.bottom - otherBounds.top) > 1):
                    bodyBounds.left = otherBounds.right
                    body.velocity[0] = 0
                    body.parentEntity.position[0] = bodyBounds.centerx - body.offset[0]

                    body.touchingDirections['left'] = True
                    if(other != None):
                        other.touchingDirections['right'] = True

                # Bottom
                if (body._moveRequest[1] > 0 and bodyPos[1] < otherPos[1] and abs(
                        bodyBounds.left - otherBounds.right) > 1 and abs(bodyBounds.right - otherBounds.left) > 1):
                    bodyBounds.bottom = otherBounds.top

                    body.touchingDirections['bottom'] = True
                    if(other != None and other.static == False and body.velocity[1] != 0):
                        other.touchingDirections['top'] = True
                        body.velocity[1] = ((body.mass-other.mass)/(body.mass+other.mass))*body.velocity[1] + ((2*other.mass)/(body.mass+other.mass))*other.velocity[1]
                        other.velocity[1] = ((2*body.mass)/(body.mass+other.mass))*body.velocity[1] - ((body.mass-other.mass)/(body.mass+other.mass))*other.velocity[1]
                    else:
                        body.velocity[1] = 0
                        body.parentEntity.position[1] = bodyBounds.centery - body.offset[1]

                # Top
                elif (body._moveRequest[1] < 0 and bodyPos[1] > otherPos[1] and abs(
                        bodyBounds.left - otherBounds.right) > 1 and abs(bodyBounds.right - otherBounds.left) > 1):
                    bodyBounds.top = otherBounds.bottom

                    body.touchingDirections['top'] = True
                    if(other != None and other.static == False and body.velocity[1] != 0):
                        other.touchingDirections['bottom'] = True
                        body.velocity[1] = ((body.mass-other.mass)/(body.mass+other.mass))*body.velocity[1] + ((2*other.mass)/(body.mass+other.mass))*other.velocity[1]
                        other.velocity[1] = ((2 * body.mass) / (body.mass + other.mass)) * body.velocity[1] - (
                                    (body.mass - other.mass) / (body.mass + other.mass)) * other.velocity[1]
                    else:
                        body.velocity[1] = 0
                        body.parentEntity.position[1] = bodyBounds.centery - body.offset[1]

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
