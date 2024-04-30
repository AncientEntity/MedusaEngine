import pygame

from engine.ecs import Component, EntitySystem, Scene
from engine.logging import Log, LOG_WARNINGS
from engine.systems.renderer import SpriteRenderer, TilemapRenderer


class PhysicsComponent(Component):
    def __init__(self,bounds=[10,10]):
        super().__init__()
        self.bounds = bounds #centered on parent entity's position
        self._moveRequest = None
        self.mapToSpriteOnStart = True
        self.touchingDirections = {'top':  False, 'bottom' : False, 'left' : False, 'right' : False}

        self.gravity : tuple(float) = None #either None or a tuple like: (0,9.84)
        self.velocity = [0,0]

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

    def ResetCollisionDirections(self):
        self.touchingDirections['left'] = False
        self.touchingDirections['right'] = False
        self.touchingDirections['top'] = False
        self.touchingDirections['bottom'] = False

class PhysicsSystem(EntitySystem):
    def __init__(self):
        super().__init__([PhysicsComponent])
    def Update(self,currentScene : Scene):
        body : PhysicsComponent

        #Physics Component Collision
        for body in currentScene.components[PhysicsComponent]:
            if(body.gravity != None):
                body.velocity[0] += body.gravity[0] * self.game.deltaTime
                body.velocity[1] += body.gravity[1] * self.game.deltaTime
            if(body.velocity[0] != 0 or body.velocity[1] != 0):
                body.Move((body.velocity[0] * self.game.deltaTime,body.velocity[1] * self.game.deltaTime))

            if(body._moveRequest == None):
                continue
            body.parentEntity.position[0] += body._moveRequest[0]
            body.parentEntity.position[1] += body._moveRequest[1]

            body.ResetCollisionDirections()

            #Physics Component Collision
            other : PhysicsComponent
            for other in currentScene.components[PhysicsComponent]:
                if(body == other):
                    continue

                bodyPos = body.parentEntity.position
                otherPos = other.parentEntity.position
                bodyBounds = pygame.Rect(bodyPos[0]-body.bounds[0]//2,bodyPos[1]-body.bounds[1]//2,body.bounds[0],body.bounds[1])
                otherBounds = pygame.Rect(otherPos[0]-other.bounds[0]//2,otherPos[1]-other.bounds[1]//2,other.bounds[0],other.bounds[1])

                self.HandlePhysicsCollision(body,bodyPos,otherPos,bodyBounds,otherBounds)

            #Tileset Collision
            for tilemapRenderer in currentScene.components[TilemapRenderer]:
                if(tilemapRenderer.tileMap == None):
                    continue

                bodyPos = body.parentEntity.position
                bodyBounds = pygame.Rect(bodyPos[0]-body.bounds[0]//2,bodyPos[1]-body.bounds[1]//2,body.bounds[0],body.bounds[1])


                topLeftOverlap = tilemapRenderer.WorldToTilePosition((bodyBounds.left,bodyBounds.top))
                bottomRightOverlap = tilemapRenderer.WorldToTilePosition((bodyBounds.right,bodyBounds.bottom))
                overlappingTiles = tilemapRenderer.GetOverlappingTilesInTileSpace(topLeftOverlap,bottomRightOverlap)

                for x in range(tilemapRenderer.tileMap.size[0]):
                    for y in range(tilemapRenderer.tileMap.size[1]):
                        c = (255,255,0)
                        for t in overlappingTiles:
                            if(tilemapRenderer.TileToWorldPosition((x,y)) == t[1]):
                                c = (255,0,0)
                        pygame.draw.rect(self.game.display,c, (tilemapRenderer.TileToWorldPosition((x,y))[0],tilemapRenderer.TileToWorldPosition((x,y))[1],16,16))


                for tile in overlappingTiles:
                    if(tile[0] == -1):
                        continue
                    if(tilemapRenderer.tileMap.tileSet[tile[0]].hasCollision):
                        otherBounds = pygame.Rect(tile[1][0], tile[1][1], tilemapRenderer.tileMap.tileSize, tilemapRenderer.tileMap.tileSize)
                        self.HandlePhysicsCollision(body,bodyPos,otherBounds.center,bodyBounds,otherBounds)

                        pygame.draw.rect(self.game.display,(0,0,0),otherBounds)

            pygame.draw.rect(self.game.display,(0,0,255),(bodyBounds.x,bodyBounds.y,bodyBounds.w,bodyBounds.h))
            body._moveRequest = None

        pygame.display.update()

    def OnEnable(self):
        body : PhysicsComponent
        for body in self.game.GetCurrentScene().components[PhysicsComponent]:
            if(body.mapToSpriteOnStart):
                body.MapToSpriteRenderer()

    def HandlePhysicsCollision(self,body,bodyPos,otherPos,bodyBounds,otherBounds):
        #If colliding handle accordingly, otherwise we have an else statement below that detects touching.
        if (bodyBounds.colliderect(otherBounds)):
            # body and other are colliding.

            # Right
            if (body._moveRequest[0] > 0 and bodyPos[0] < otherPos[0] and abs(
                    bodyBounds.top - otherBounds.bottom) > 1 and abs(bodyBounds.bottom - otherBounds.top) > 1):
                bodyPos[0] = otherBounds.left - bodyBounds.width // 2
                body.velocity[0] = 0
                body.touchingDirections['right'] = True
            # Left
            elif (body._moveRequest[0] < 0 and bodyPos[0] > otherPos[0] and abs(
                    bodyBounds.top - otherBounds.bottom) > 1 and abs(bodyBounds.bottom - otherBounds.top) > 1):
                bodyPos[0] = otherBounds.right + bodyBounds.width // 2
                body.velocity[0] = 0
                body.touchingDirections['left'] = True

            # Bottom
            if (body._moveRequest[1] > 0 and bodyPos[1] < otherPos[1] and abs(
                    bodyBounds.left - otherBounds.right) > 1 and abs(bodyBounds.right - otherBounds.left) > 1):
                bodyPos[1] = otherBounds.top - bodyBounds.height // 2
                body.velocity[1] = 0
                body.touchingDirections['bottom'] = True
            # Top
            elif (body._moveRequest[1] < 0 and bodyPos[1] > otherPos[1] and abs(
                    bodyBounds.left - otherBounds.right) > 1 and abs(bodyBounds.right - otherBounds.left) > 1):
                bodyPos[1] = otherBounds.bottom + bodyBounds.height // 2
                body.velocity[1] = 0
                body.touchingDirections['top'] = True
        else:  # If not colliding with it, we see if it is touching
            if (abs(bodyBounds.left - otherBounds.right) <= 2):
                body.touchingDirections['left'] = True
            if (abs(bodyBounds.right - otherBounds.left) <= 2):
                body.touchingDirections['right'] = True
            if (abs(bodyBounds.top - otherBounds.bottom) <= 2):
                body.touchingDirections['top'] = True
            if (abs(bodyBounds.bottom - otherBounds.top) <= 2):
                body.touchingDirections['bottom'] = True