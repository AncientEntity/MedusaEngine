import random

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
        self.layerObjects : list = []
        self.layerObjectsDict : dict = {}
    def Init(self):
        self.Clear()
        self.layerObjects = []

        #Load Tile Layers
        for layer in self.mapJson["layers"]:
            #Get layer offset (if it exists)
            offset = [0, 0]
            if ("offsetx" in layer and "offsety" in layer):
                offset = [layer["offsetx"], layer["offsety"]]

            if("objects" in layer):
                self.LoadObjectLayer(layer,offset)
            else:
                #Tile Layer
                self.CreateEntity("WORLD-"+layer["name"], offset, components=[self.LoadTileLayer(layer)])

        self.LevelStart()
        super().Init()

    def LevelStart(self):
        pass

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

    def LoadObjectLayer(self,layer,offset): #todo here, must place down all objects found in objectMap and must put all objects into self.objects and make a function to get object(s) by name
        for object in layer["objects"]:
            self.layerObjects.append(object)
            object["position"] = tiled.ObjectPositionToLocalPosition(object["x"]+offset[0],object["y"]+offset[1],self.mapJson)
            if(object["name"] not in self.layerObjectsDict):
                self.layerObjectsDict[object["name"]] = []
            self.layerObjectsDict[object["name"]].append(object)
            if(self.objectMap != None and object["name"] in self.objectMap):
                objectInstance = self.objectMap[object["name"]](self) #Create objectInstance from creator function
                objectInstance.position = object["position"]

    def GetPropertyOfLayer(self,layer,propertyName):
        if("properties" in layer):
            for prop in layer["properties"]:
                if(prop["name"] == propertyName):
                    return prop["value"]
        return None

    #Returns the first found tiled object.
    def GetTiledObjectByName(self,objName):
        if(objName in self.layerObjectsDict):
            return self.layerObjectsDict[objName][0]
        return None

    #Returns all the tiled objects with name
    def GetTiledObjectsByName(self, objName):
        if(objName in self.layerObjectsDict):
            return self.layerObjectsDict[objName]

    def GetRandomTiledObjectByName(self,objName):
        if(objName in self.layerObjectsDict):
            return self.layerObjectsDict[objName][random.randint(0,len(self.layerObjectsDict[objName])-1)]
        return None