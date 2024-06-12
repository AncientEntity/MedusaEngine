from engine.components.rendering.renderercomponent import RendererComponent
from engine.datatypes.sprites import Sprite
from engine.logging import Log, LOG_ERRORS
from engine.datatypes.spritesheet import SpriteSheet

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
    def SetTileSetFromSpriteSheet(self,spriteSheet : SpriteSheet,alpha=255):
        if(spriteSheet.splitType == 'size'):
            for x in range(spriteSheet.xCount):
                for y in range(spriteSheet.yCount):
                    hashIndex = y*spriteSheet.xCount+x
                    self.tileSet[hashIndex] = Sprite(spriteSheet[(x,y)])
                    self.tileSet[hashIndex].SetAlpha(alpha)

        elif(spriteSheet.splitType == 'map'):
            for key,value in spriteSheet.sprites.items():
                self.tileSet[key] = Sprite(value)
        else:
            Log("Unknown sprite sheet split type: ",spriteSheet.splitType,LOG_ERRORS)

class TilemapRenderer(RendererComponent):
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

    #Returns the 2D index of a tile from a point, or None when it is outside of the bounds.
    def GetTileIndexAtWorldPoint(self, x, y):
        tilePosition = self.WorldToTilePosition((x,y))
        if(tilePosition[0] < 0 or tilePosition[1] < 0 or tilePosition[0] >= self.tileMap.size[0] or tilePosition[1] >= self.tileMap.size[1]):
            return None #Outside bounds
        return tilePosition

