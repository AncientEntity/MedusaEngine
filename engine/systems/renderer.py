import pygame.display

from engine.ecs import EntitySystem, Scene, Component
from engine.logging import Log, LOG_ERRORS
from engine.tools.spritesheet import SpriteSheet
import time

def CenterToTopLeftPosition(centerPosition, surface : pygame.Surface):
    return [centerPosition[0]-surface.get_width()//2,centerPosition[1]-surface.get_height()//2]

class Sprite:
    def __init__(self,filePath):
        self.sprite = pygame.image.load(filePath)
    def GetSprite(self):
        return self.sprite

class AnimatedSprite(Sprite):
    def __init__(self,sprites,fps):
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

def GetSprite(sprite):
    if(isinstance(sprite,pygame.Surface)):
        return sprite
    else:
        return sprite.GetSprite()

class SpriteRenderer(Component):
    def __init__(self, sprite : Sprite or pygame.Surface):
        self.sprite = sprite

class Tilemap:
    def __init__(self,size):
        self.size = size
        self.tileSize = 50
        self.map = []
        self.tileSet : dict = dict() #{0: SURFACE, 1 : SURFACE, 2 : SURFACE} or {"orc_1" : SURFACE, "orc_2" : SURFACE} etc

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
                    self.tileSet[i] = spriteSheet[(x,y)]
                    i += 1
        elif(spriteSheet.splitType == 'map'):
            for key,value in spriteSheet.sprites.items():
                self.tileSet[key] = value
        else:
            Log("Unknown sprite sheet split type: ",spriteSheet.splitType,LOG_ERRORS)

class TilemapRenderer(Component):
    def __init__(self,tileMap=None):
        super().__init__()
        self.tileMap = tileMap


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
        self.debug = False

        RenderingSystem.instance = self
    def OnEnable(self):
        self._screenSize = [self.game.display.get_width(),self.game.display.get_height()]
        self._scaledScreenSize = [self.game.display.get_width() // self.renderScale,self.game.display.get_height() // self.renderScale]
        self._renderTarget = pygame.Surface(self._scaledScreenSize)
    def Update(self,currentScene : Scene):
        self._renderTarget.fill(self.backgroundColor)

        #TileMapRenderer
        for tileMapRenderer in currentScene.components[TilemapRenderer]:
            if(tileMapRenderer.tileMap == None or tileMapRenderer.tileMap.tileSet == None):
                continue
            centeredOffset = [tileMapRenderer.parentEntity.position[0] - (tileMapRenderer.tileMap.size[0]*tileMapRenderer.tileMap.tileSize)//2,tileMapRenderer.parentEntity.position[1] - (tileMapRenderer.tileMap.size[1]*tileMapRenderer.tileMap.tileSize)//2]
            for x in range(tileMapRenderer.tileMap.size[0]):
                for y in range(tileMapRenderer.tileMap.size[1]):
                    if(tileMapRenderer.tileMap.map[x][y] == -1): #Empty tile
                        continue
                    targetSprite = GetSprite(tileMapRenderer.tileMap.tileSet[tileMapRenderer.tileMap.map[x][y]])
                    spritePosition = [centeredOffset[0]+(x*tileMapRenderer.tileMap.tileSize),centeredOffset[1]+(y*tileMapRenderer.tileMap.tileSize)]
                    self._renderTarget.blit(targetSprite,[spritePosition[0]-self.cameraPosition[0],spritePosition[1]-self.cameraPosition[1]])

        #SpriteRenderer
        for spriteRenderer in currentScene.components[SpriteRenderer]:
            if(spriteRenderer.sprite == None):# or False == self.IsOnScreen(spriteRenderer)):
                continue
            actualSprite = GetSprite(spriteRenderer.sprite)
            if(actualSprite == None):
                continue
            finalPosition = self.FinalPositionOfSprite(spriteRenderer.parentEntity.position,actualSprite)
            self._renderTarget.blit(actualSprite,finalPosition)

            if(self.debug): #If debug draw bounds of spriterenderers
                pygame.draw.rect(self._renderTarget,(255,0,0),pygame.Rect(finalPosition[0],finalPosition[1],spriteRenderer.sprite.get_width(),spriteRenderer.sprite.get_height()),width=1)

        self.game.display.blit(pygame.transform.scale(self._renderTarget,(self._screenSize[0],self._screenSize[1])),(0,0))
        pygame.display.update()
    def FinalPositionOfSprite(self,position,sprite):
        topLeftPosition = CenterToTopLeftPosition(position, sprite)
        return [topLeftPosition[0] - self.cameraPosition[0], topLeftPosition[1] - self.cameraPosition[1]]

    #Doesn't work so disabled for now.
    def IsOnScreen(self,spriteRenderer : SpriteRenderer) -> bool:

        #screen bounds with camera, xywh
        screenBounds = pygame.Rect(self.cameraPosition[0] - self._scaledScreenSize[0]//2,self.cameraPosition[1] - self._scaledScreenSize[1]//2,self._scaledScreenSize[0],self._scaledScreenSize[1])
        spriteBounds = pygame.Rect(spriteRenderer.parentEntity.position[0]-spriteRenderer.sprite.get_width()//2,spriteRenderer.parentEntity.position[1]-spriteRenderer.sprite.get_height()//2,spriteRenderer.sprite.get_width(),spriteRenderer.sprite.get_height())

        #pygame.draw.rect(self._renderTarget,(255,0,0),spriteBounds)
        #pygame.draw.rect(self._renderTarget,(0,255,0),screenBounds)
        return screenBounds.colliderect(spriteBounds)
