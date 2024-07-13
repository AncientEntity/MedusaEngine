from engine.components.rendering.tilemaprenderer import Tilemap, TilemapRenderer


class TilemapPathfinder:
    def __init__(self, tilemaps : list[TilemapRenderer], blockingPhysicsLayers : list[int], avoidEmptyTiles=True):
        self.tilemaps : list[TilemapRenderer] = tilemaps
        self.blockingPhysicsLayers = blockingPhysicsLayers # physics layers the pathfinder determines as blocking.
                                                           # give your tiled map layer the property "physicsLayer"
                                                           # to give it a physics layer value.
        self.avoidEmptyTiles = avoidEmptyTiles # Whether it should avoid empty tiles (-1). All layers have to
                                               # be empty for it to consider a tile empty.
    def IsTileBlocking(self, tileIndex) -> bool:
        isEmpty = True
        for layer in self.tilemaps:
            tileID = layer.tileMap.GetTileID(tileIndex[0],tileIndex[1])
            if(tileID == -1):
                continue
            else:
                isEmpty = False
                if tileID in self.blockingPhysicsLayers:
                    return True
        return isEmpty and self.avoidEmptyTiles
