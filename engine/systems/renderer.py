import math

import pygame.display

from engine.ecs import EntitySystem, Scene, Component
from engine.logging import Log, LOG_ERRORS
from engine.tools.spritesheet import SpriteSheet
import time

def CenterToTopLeftPosition(centerPosition, surface : pygame.Surface):
    return [centerPosition[0]-surface.get_width()//2,centerPosition[1]-surface.get_height()//2]

def GetSprite(sprite):
    if(isinstance(sprite,pygame.Surface)):
        return sprite
    else:
        return sprite.GetSprite()

class Sprite:
    def __init__(self,filePathOrSurface : str or pygame.Surface):
        if(isinstance(filePathOrSurface,str)):
            if(filePathOrSurface != ""):
                self.sprite = pygame.image.load(filePathOrSurface)
            else:
                self.sprite = None
        elif(isinstance(filePathOrSurface,pygame.Surface)):
            self.sprite = filePathOrSurface
        self._flipX = False
        self.ignoreCollision = False
    def GetSprite(self):
        return self.sprite
    def FlipX(self,flipped):
        if(flipped == self._flipX):
            return

        self._flipX = flipped
        if(isinstance(self.sprite,pygame.Surface)):
            self.sprite = pygame.transform.flip(self.sprite,True,False)
        else:
            self.sprite.FlipX(flipped)
    def get_width(self):
        return self.sprite.get_width()
    def get_height(self):
        return self.sprite.get_height()

class AnimatedSprite(Sprite):
    def __init__(self,sprites,fps):
        super().__init__("")
        self.timer = 0
        self.sprites = sprites
        self.fps = fps
        self.lastTime = time.time()
    def GetSprite(self):
        self.timer += (time.time() - self.lastTime)
        self.lastTime = time.time()
        targetSprite = self.sprites[int((self.timer * self.fps) % len(self.sprites))]
        if isinstance(targetSprite, pygame.Surface):
            return targetSprite
        elif(isinstance(targetSprite,Sprite)):
            return targetSprite.GetSprite()
    def FlipX(self,flipped):
        if(flipped == self._flipX):
            return

        self._flipX = flipped
        for i in range(len(self.sprites)):
            if(isinstance(self.sprites[i],pygame.Surface)):
                self.sprites[i] = pygame.transform.flip(self.sprites[i],True,False)
            else:
                self.sprites[i].FlipX(flipped)
    def get_width(self):
        return self.GetSprite().get_width()
    def get_height(self):
        return self.GetSprite().get_height()

class SpriteRenderer(Component):
    def __init__(self, sprite : Sprite or pygame.Surface):
        self.sprite = sprite


class Tilemap:
    def __init__(self,size):
        self.size = size
        self.tileSize = 50
        self.map = []
        self.tileSet : dict = dict() #{0: Sprite, 1 : Sprite, 2 : Sprite} or {"orc_1" : Sprite, "orc_2" : Sprite} etc dont put surfaces in

        for x in range(self.size[0]):
            xRow = []
            for i in range(self.size[1]):
                xRow.append(-1)
            self.map.append(xRow)
    def SetTile(self,tileID : int, x,y):
        if(x < self.size[0] and y < self.size[1] and (tileID in self.tileSet or tileID == -1)):
            self.map[x][y] = tileID
        else:
            Log("Invalid spot to set tile or invalid tileID."+str(tileID),LOG_ERRORS)
    def SetTileSetFromSpriteSheet(self,spriteSheet : SpriteSheet):
        if(spriteSheet.splitType == 'size'):
            i = 0
            for x in range(spriteSheet.xCount):
                for y in range(spriteSheet.yCount):
                    self.tileSet[i] = Sprite(spriteSheet[(y,x)])
                    i += 1
        elif(spriteSheet.splitType == 'map'):
            for key,value in spriteSheet.sprites.items():
                self.tileSet[key] = Sprite(value)
        else:
            Log("Unknown sprite sheet split type: ",spriteSheet.splitType,LOG_ERRORS)

class TilemapRenderer(Component):
    def __init__(self,tileMap=None):
        super().__init__()
        self.tileMap = tileMap
        self.physicsLayer = 0
    def WorldToRoundedPosition(self, worldPosition): #Rounds a world position to a world position where the tile is.
        return [(worldPosition[0]-self.parentEntity.position[0])//self.tileMap.tileSize*self.tileMap.tileSize,(worldPosition[1]-self.parentEntity.position[1])//self.tileMap.tileSize*self.tileMap.tileSize]
    def WorldToTilePosition(self,worldPosition):
        return [(worldPosition[0]-self.parentEntity.position[0]+(self.tileMap.size[0]//2*self.tileMap.tileSize))//self.tileMap.tileSize,(worldPosition[1]-self.parentEntity.position[1]+(self.tileMap.size[1]//2*self.tileMap.tileSize))//self.tileMap.tileSize]
    def TileToWorldPosition(self,tilePosition):
        return [tilePosition[0]*self.tileMap.tileSize+self.parentEntity.position[0]-(self.tileMap.size[0]/2*self.tileMap.tileSize),tilePosition[1]*self.tileMap.tileSize+self.parentEntity.position[1]-(self.tileMap.size[1]/2*self.tileMap.tileSize)]

    def GetOverlappingTilesInTileSpace(self,topLeft,bottomRight):
        tiles = []
        for x in range(topLeft[0]-2,bottomRight[0]+2):
            for y in range(topLeft[1]-2,bottomRight[1]+2):
                if(x >= 0 and y >= 0 and x < self.tileMap.size[0] and y < self.tileMap.size[1]):
                    worldPos = self.TileToWorldPosition((x,y))
                    tiles.append([self.tileMap.map[x][y],(worldPos[0],worldPos[1])])
        return tiles



class RenderingSystem(EntitySystem):
    instance = None
    def __init__(self):
        super().__init__([SpriteRenderer,TilemapRenderer])
        self.cameraPosition = [0,0]
        self.renderScale = 3
        self.backgroundColor = (255,255,255)
        self._renderTarget = None
        self._screenSize = None
        self._scaledScreenSize = None
        self._scaledHalfSize = None
        self.debug = False

    def OnEnable(self):
        RenderingSystem.instance = self
        self._screenSize = [self.game.display.get_width(),self.game.display.get_height()]
        self._scaledScreenSize = [self.game.display.get_width() // self.renderScale,self.game.display.get_height() // self.renderScale]
        self._scaledHalfSize = [self._scaledScreenSize[0]//2,self._scaledScreenSize[1]//2]
        self._renderTarget = pygame.Surface(self._scaledScreenSize)
    def Update(self,currentScene : Scene):
        self._renderTarget.fill(self.backgroundColor)
        self.cameraPosition = [math.floor(self.cameraPosition[0]),math.floor(self.cameraPosition[1])]

        #TileMapRenderer
        for tileMapRenderer in currentScene.components[TilemapRenderer]:
            if(tileMapRenderer.tileMap == None or tileMapRenderer.tileMap.tileSet == None):
                continue
            centeredOffset = [tileMapRenderer.parentEntity.position[0] - (tileMapRenderer.tileMap.size[0]*tileMapRenderer.tileMap.tileSize)//2,tileMapRenderer.parentEntity.position[1] - (tileMapRenderer.tileMap.size[1]*tileMapRenderer.tileMap.tileSize)//2]
            for x in range(tileMapRenderer.tileMap.size[0]):
                for y in range(tileMapRenderer.tileMap.size[1]):
                    if(tileMapRenderer.tileMap.map[x][y] == -1): #Empty tile
                        continue

                    #Get world position then the left anchored screen position
                    worldPosition = [centeredOffset[0]+(x*tileMapRenderer.tileMap.tileSize),centeredOffset[1]+(y*tileMapRenderer.tileMap.tileSize)]
                    leftAnchoredScreenPosition = self.WorldToScreenPosition(worldPosition)

                    if(False == self.IsOnScreenRect(pygame.Rect(worldPosition[0], worldPosition[1],tileMapRenderer.tileMap.tileSize,tileMapRenderer.tileMap.tileSize))):
                        continue

                    targetSprite = GetSprite(tileMapRenderer.tileMap.tileSet[tileMapRenderer.tileMap.map[x][y]])
                    self._renderTarget.blit(targetSprite,leftAnchoredScreenPosition)

        #SpriteRenderer
        for spriteRenderer in currentScene.components[SpriteRenderer]:
            if(spriteRenderer.sprite == None):
                continue

            actualSprite = GetSprite(spriteRenderer.sprite)
            #Validate if we found an actual sprite
            if(actualSprite == None):
                continue

            #Verify what is being drawn is on the screen
            if(False == self.IsOnScreenSprite(actualSprite, spriteRenderer.parentEntity.position)):
                continue

            finalPosition = self.FinalPositionOfSprite(spriteRenderer.parentEntity.position,actualSprite)
            self._renderTarget.blit(actualSprite,finalPosition)

            if(self.debug): #If debug draw bounds of spriterenderers
                pygame.draw.rect(self._renderTarget,(255,0,0),pygame.Rect(finalPosition[0]-1,finalPosition[1],actualSprite.get_width(),actualSprite.get_height()),width=1)

        #Finally blit the render target onto the final display.
        self.game.display.blit(pygame.transform.scale(self._renderTarget,(self._screenSize[0],self._screenSize[1])),(0,0))
        pygame.display.update()

    def WorldToScreenPosition(self,position):
        return [position[0] - self.cameraPosition[0] + self._scaledHalfSize[0], position[1] - self.cameraPosition[1] + self._scaledHalfSize[1]]

    def FinalPositionOfSprite(self,position,sprite):
        topLeftPosition = CenterToTopLeftPosition(position, sprite)
        return self.WorldToScreenPosition(topLeftPosition)

    def IsOnScreenSprite(self, sprite : pygame.Surface, position) -> bool:
        return self.IsOnScreenRect(pygame.Rect(position[0]-sprite.get_width()//2,position[1]-sprite.get_height()//2,sprite.get_width(),sprite.get_height()))

    def IsOnScreenRect(self,rect : pygame.Rect):
        screenBounds = pygame.Rect(self.cameraPosition[0] - self._scaledHalfSize[0],self.cameraPosition[1] - self._scaledHalfSize[1],self._scaledScreenSize[0],self._scaledScreenSize[1])
        return screenBounds.colliderect(rect)

    def DebugDrawWorldRect(self,color,rect):
        worldP = self.WorldToScreenPosition((rect.x,rect.y))
        pygame.draw.rect(self._renderTarget,(255,0,0),(worldP[0],worldP[1],rect.w,rect.h))