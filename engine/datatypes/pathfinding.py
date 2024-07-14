from engine.components.rendering.tilemaprenderer import TilemapRenderer
from engine.tools.math import Distance
import time

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
                if layer.physicsLayer in self.blockingPhysicsLayers:
                    return True
        return isEmpty and self.avoidEmptyTiles

    def Solve(self, startIndex, endIndex):
        nodes = self.CreateEmptyMap()
        headIndexes = [startIndex]

        def IsValidIndex(index):
            return index[0] >= 0 and index[1] >= 0 and index[0] < len(nodes) and index[1] < len(nodes[0]) and not self.IsTileBlocking(index)

        if not IsValidIndex(startIndex) or not IsValidIndex(endIndex):
            return None

        def CalculateNodeData(nodeIndex, prevNode):
            if(nodes[nodeIndex[0]][nodeIndex[1]] != None):
                return
            gValue = Distance(nodeIndex,startIndex)
            fValue = Distance(nodeIndex,endIndex)
            nodes[nodeIndex[0]][nodeIndex[1]] = (gValue,fValue,gValue+fValue, prevNode)

        def ConstructPath():
            curIndex = endIndex
            path = [endIndex]
            while(curIndex != startIndex):
                previous = nodes[curIndex[0]][curIndex[1]][3]
                path.insert(0,previous)
                curIndex = previous
            return path
        def GetNextValidIndexes(index):
            surroundingIndexes = []

            # Up
            if IsValidIndex((index[0],index[1]-1)):
                surroundingIndexes.append((index[0],index[1]-1))
            # Down
            if IsValidIndex((index[0],index[1]+1)):
                surroundingIndexes.append((index[0],index[1]+1))
            # Left
            if IsValidIndex((index[0]-1,index[1])):
                surroundingIndexes.append((index[0]-1,index[1]))
            # Right
            if IsValidIndex((index[0]+1,index[1])):
                surroundingIndexes.append((index[0]+1,index[1]))
            # TopLeft
            if IsValidIndex((index[0]-1,index[1]-1)):
                surroundingIndexes.append((index[0]-1,index[1]-1))
            # TopRight
            if IsValidIndex((index[0]+1,index[1]-1)):
                surroundingIndexes.append((index[0]+1,index[1]-1))
            # BottomLeft
            if IsValidIndex((index[0]-1,index[1]+1)):
                surroundingIndexes.append((index[0]-1,index[1]+1))
            # BottomRight
            if IsValidIndex((index[0]+1,index[1]+1)):
                surroundingIndexes.append((index[0]+1,index[1]+1))

            newIndexes = []
            for index in surroundingIndexes:
                if nodes[index[0]][index[1]] == None:
                    newIndexes.append(index)
            return newIndexes

        def SortNewHeadIndex(index, prevIndex):
            if(nodes[index[0]][index[1]] != None):
                return
            else:
                CalculateNodeData(index, prevIndex)
                i = 0
                while i < len(headIndexes) and nodes[headIndexes[i][0]][headIndexes[i][1]][2] < nodes[index[0]][index[1]][2]:
                    i += 1
                headIndexes.insert(i,index)


        CalculateNodeData(startIndex, None)

        while len(headIndexes) > 0:
            for index in headIndexes[:]:
                if(index[0] == endIndex[0] and index[1] == endIndex[1]):
                    return ConstructPath() # Reconstruct the path and return
                else:
                    nextValidIndexes = GetNextValidIndexes(index)
                    for newIndex in nextValidIndexes:
                        SortNewHeadIndex(newIndex,index)

                headIndexes.remove(index)


        return None # No path found


    def CreateEmptyMap(self):
        nodes = []
        for x in range(len(self.tilemaps[0].tileMap.map)):
            row = []
            nodes.append(row)
            for y in range(len(self.tilemaps[0].tileMap.map[0])):
                row.append(None)
        return nodes


# TilePathfinderHelper
# Caches the solved path and only searches again if the path becomes invalid, or if the start/end change.
# It's possible the solved path will change if the tilemap changes over time and it doesn't update.
class TilePathfinderHelper:
    def __init__(self, tilemapPathfinder : TilemapPathfinder):
        self.pathfinder : TilemapPathfinder = tilemapPathfinder
        self.cachedPath = None
        self.cachedStart = None
        self.cachedEnd = None

        self.cacheLifetime = 10 # If the cache has been alive for more than X seconds, resolve the path regardless
        self.cacheSolveTime = 0
    def Solve(self, startIndex, endIndex):
        startIndex = tuple(startIndex); endIndex = tuple(endIndex)
        def IsPathValid(path):
            for index in path:
                if self.pathfinder.IsTileBlocking(index):
                    return False
            return True

        if(self.cachedPath == None or self.cachedStart != startIndex or self.cachedEnd != endIndex or time.time() - self.cacheSolveTime > self.cacheLifetime or not IsPathValid(self.cachedPath)):
            self.cachedPath = self.pathfinder.Solve(startIndex,endIndex)
            self.cachedStart = startIndex
            self.cachedEnd = endIndex
            self.cacheSolveTime = time.time()
        return self.cachedPath
