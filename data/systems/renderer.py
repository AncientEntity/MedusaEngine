import pygame.display

from data.ecs import EntitySystem, Scene, Component
from data.logging import Log, LOG_ERRORS
from data.tools.spritesheet import SpriteSheet

def CenterToTopLeftPosition(centerPosition, surface : pygame.Surface):
    return [centerPosition[0]-surface.get_width(),centerPosition[1]-surface.get_height()]

class SpriteRenderer(Component):
    def __init__(self, parentEntity, sprite : pygame.Surface):
        super().__init__(parentEntity)
        self.sprite = sprite

class Tilemap:
    def __init__(self,size):
        self.size = size
        self.tileSize = 50
        self.map = []
        self.tileSet : dict = dict() #{0: SURFACE, 1 : SURFACE, 2 : SURFACE} etc

        for x in range(self.size[0]):
            xRow = []
            for i in range(self.size[1]):
                xRow.append(-1)
            self.map.append(xRow)
    def SetTile(self,tileID : int, x,y):
        if(x < self.size[0] and y < self.size[1] and (tileID in self.tileSet or tileID == -1)):
            self.map[x][y] = tileID
        else:
            Log("Invalid spot to set tile or invalid tileID.",LOG_ERRORS)

class TilemapRenderer(Component):
    def __init__(self, parentEntity):
        super().__init__(parentEntity)
        self.tileMap = None


class RendererSystem(EntitySystem):
    def __init__(self):
        super().__init__([SpriteRenderer,TilemapRenderer])
        self.cameraPosition = [0,0]
    def Update(self,currentScene : Scene):
        currentScene.game.display.fill((255,255,255))

        for tileMapRenderer in currentScene.components[TilemapRenderer]:
            if(tileMapRenderer.tileMap == None or tileMapRenderer.tileMap.tileSet == None):
                continue
            centeredOffset = [tileMapRenderer.parentEntity.position[0] - (tileMapRenderer.tileMap.size[0]*tileMapRenderer.tileMap.tileSize)//2,tileMapRenderer.parentEntity.position[1] - (tileMapRenderer.tileMap.size[1]*tileMapRenderer.tileMap.tileSize)//2]
            for x in range(tileMapRenderer.tileMap.size[0]):
                for y in range(tileMapRenderer.tileMap.size[1]):
                    if(tileMapRenderer.tileMap.map[x][y] == -1): #Empty tile
                        continue
                    targetSprite = tileMapRenderer.tileMap.tileSet[tileMapRenderer.tileMap.map[x][y]]
                    spritePosition = [centeredOffset[0]+(x*tileMapRenderer.tileMap.tileSize),centeredOffset[1]+(y*tileMapRenderer.tileMap.tileSize)]
                    currentScene.game.display.blit(targetSprite,spritePosition)

        for spriteRenderer in currentScene.components[SpriteRenderer]:
            if(spriteRenderer.sprite == None):
                continue

            currentScene.game.display.blit(spriteRenderer.sprite,self.FinalPositionOfSprite(spriteRenderer.parentEntity.position,spriteRenderer.sprite))

        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                currentScene.game.Quit()

        pygame.display.update()
    def FinalPositionOfSprite(self,position,sprite):
        topLeftPosition = CenterToTopLeftPosition(position, sprite)
        return [topLeftPosition[0] - self.cameraPosition[0], topLeftPosition[1] - self.cameraPosition[1]]