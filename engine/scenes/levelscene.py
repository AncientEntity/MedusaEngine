from engine.ecs import Scene
from engine.systems import renderer, physics
from engine.systems.renderer import TilemapRenderer, Tilemap
from engine.tools.spritesheet import SpriteSheet
import engine.tools.tiled as tiled
from game import prefabs


class LevelScene(Scene):

    #tiledFilePath - file to the exported tiled map json
    #worldTileset - the spritesheet containing the tiles
    #objectMap - a dict that goes from objectName to the entity that should be created there.
    #            ie "SPAWN": CreatePlayer, where CreatePlayer is a function that takes in a Scene (self) and returns an Entity
    def __init__(self, tiledFilePath : str, worldTileset : SpriteSheet, objectMap : dict):
        super().__init__()
        self.systems = [renderer.RenderingSystem(),physics.PhysicsSystem()]
        self.mapJson = tiled.TiledGetRawMapData(tiledFilePath)
        self.tileMapLayers : list[TilemapRenderer] = []
        self.worldTileset = worldTileset

        self.objectMap = objectMap
        self.objects : dict = []
    def Init(self):
        self.Clear()
        self.objects = []

        tilemapRenderers = []
        #Load tile layers
        for layer in self.mapJson["layers"]:
            if("objects" in layer):
                self.LoadObjectLayer(layer)
            else:
                #Tile Layer
                tilemapRenderers.append(self.LoadTileLayer(layer))

        #Create containing entity for all the tilemap layers
        self.CreateEntity("WORLD", [0, 0], components=tilemapRenderers)

        super().Init()

    def LoadTileLayer(self,layer):
        size = (layer["width"], layer["height"])
        tileSize = self.mapJson["tilewidth"]

        physicsLayer = self.GetPropertyOfLayer(layer, "physicsLayer")

        # Create Tilemap for it.
        newMap = Tilemap(size)
        newMap.tileSize = tileSize
        mapDataRowed = newMap.map
        newMap.map = mapDataRowed
        newMap.SetTileSetFromSpriteSheet(self.worldTileset)
        mapDataIndex = 0
        mapData = layer["data"]
        for y in range(size[1]):
            for x in range(size[0]):
                newMap.SetTile(mapData[mapDataIndex] - 1, x, y)  # Decrement every value in mapData as tiled uses 0 as nothing but we use -1 as nothing.
                mapDataIndex += 1
        # Put tilemap into a renderer
        tileMapRenderer = TilemapRenderer(newMap)
        if (physicsLayer == None):
            tileMapRenderer.physicsLayer = -1
        else:
            tileMapRenderer.physicsLayer = physicsLayer
        return tileMapRenderer

    def LoadObjectLayer(self,layer): #todo here, must place down all objects found in objectMap and must put all objects into self.objects and make a function to get object(s) by name
        for object in layer["objects"]:
            self.objects.append(object)
            if(self.objectMap != None and object["name"] in self.objectMap):
                objectInstance = self.objectMap[object["name"]](self) #Create objectInstance from creator function
                objectInstance.position = tiled.ObjectPositionToLocalPosition(object["x"],object["y"],self.mapJson)


    def GetPropertyOfLayer(self,layer,propertyName):
        if("properties" in layer):
            for prop in layer["properties"]:
                if(prop["name"] == propertyName):
                    return prop["value"]
        return None