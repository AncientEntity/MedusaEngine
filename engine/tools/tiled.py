#This reads JSON exported Tiled tilemaps
#More info: https://www.mapeditor.org/
import json
import engine.systems.renderer
from engine.datatypes.spritesheet import SpriteSheet

def TiledGetRawMapData(mapFilePath):
    tileFile = open(mapFilePath, "r")
    fileData = tileFile.read()
    tileFile.close()
    return json.loads(fileData)

def TiledGetRawMapDataLayer(mapFilePath, layerName):
    tileJson = TiledGetRawMapData(mapFilePath)

    #Find layer and the map data within
    mapData = None
    size = None
    for layer in tileJson["layers"]:
        if(layer["name"] == layerName):
            mapData = layer["data"]
            size = (layer["width"],layer["height"])
            break
    return mapData, size

def TiledGetTileMapFromTiledJSON(mapFilePath, layerName, tileSpriteSheet : SpriteSheet):

    mapData, size = TiledGetRawMapDataLayer(mapFilePath, layerName)

    #Now split it up into rows as tiled stores it all in 1 massive array instead of a 2D array.

    newMap = engine.systems.renderer.Tilemap(size)
    mapDataRowed = newMap.map
    newMap.map = mapDataRowed
    newMap.SetTileSetFromSpriteSheet(tileSpriteSheet)
    mapDataIndex = 0
    for y in range(size[1]):
        for x in range(size[0]):
            newMap.SetTile(mapData[mapDataIndex]-1,x,y) #Decrement every value in mapData as tiled uses 0 as nothing but we use -1 as nothing.
            mapDataIndex += 1
    return newMap

def TiledGetObjectsFromTiledJSON(mapFilePath, layerName):
    tileFile = open(mapFilePath, "r")
    fileData = tileFile.read()
    tileFile.close()
    tileJson = json.loads(fileData)

    objectList = None
    for layer in tileJson["layers"]:
        if(layer["name"] == layerName):
            objectList = layer["objects"]
            break

    #Normalize a position entry relative to the tilemap (so 0,0 is the tilemaps position)
    for obj in objectList:
        obj["position"] = ObjectPositionToLocalPosition(obj["x"],obj["y"],tileJson)

    return objectList

def ObjectPositionToLocalPosition(x,y,tileJson):
    return [x-tileJson["tilewidth"]*tileJson["width"]//2,y-tileJson["tilewidth"]*tileJson["height"]//2]

def TiledGetObjectByName(objectList, objectName):
    for obj in objectList:
        if(obj["name"] == objectName):
            return obj
    return None