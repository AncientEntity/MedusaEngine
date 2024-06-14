from engine.components.rendering.tilemaprenderer import TilemapRenderer
from engine.ecs import EntitySystem, Component, Scene
from engine.scenes.levelscene import LevelScene
from engine.tools.math import Distance
from game.components.ConsumerComponent import ConsumerComponent
from game.components.ItemComponent import ItemComponent
from game.constants import ConveyorPlaceable
import random


class ItemSystem(EntitySystem):
    def __init__(self):
        super().__init__([ItemComponent,ConsumerComponent])  # Put target components here
        self.objectLayer : TilemapRenderer = None
        self.conveyorSpeed = 35

        self.consumers = []

    def Update(self, currentScene: LevelScene):
        item : ItemComponent
        for item in currentScene.components[ItemComponent]:
            itemTileIndex = self.objectLayer.WorldPointToTileIndexSafe((item.parentEntity.position[0],item.parentEntity.position[1]))
            if(itemTileIndex == None):
                continue
            overlappingTileId = self.objectLayer.tileMap.GetTileID(int(itemTileIndex[0]),int(itemTileIndex[1]))
            if(overlappingTileId != -1):
                self.HandleItem(item, overlappingTileId, self.objectLayer.TileIndexToWorldPosition(itemTileIndex,True), currentScene)

    def HandleItem(self,item : ItemComponent,overlappingTileId : int, roundedPosition, currentScene : LevelScene):
        targetX = False
        targetY = False
        if (overlappingTileId == ConveyorPlaceable.tiles[0]):  # Move right
            item.parentEntity.position[0] += self.game.deltaTime * self.conveyorSpeed
            targetY = True
        elif (overlappingTileId == ConveyorPlaceable.tiles[1]):  # Move down
            item.parentEntity.position[1] += self.game.deltaTime * self.conveyorSpeed
            targetX = True
        elif (overlappingTileId == ConveyorPlaceable.tiles[2]):  # Move left
            item.parentEntity.position[0] -= self.game.deltaTime * self.conveyorSpeed
            targetY = True
        elif (overlappingTileId == ConveyorPlaceable.tiles[3]):  # Move up
            item.parentEntity.position[1] -= self.game.deltaTime * self.conveyorSpeed
            targetX = True

        if(targetY):
            item.parentEntity.position[1] = item.parentEntity.position[1] - (8 * self.game.deltaTime) * (item.parentEntity.position[1] - (roundedPosition[1]))
        if(targetX):
            item.parentEntity.position[0] = item.parentEntity.position[0] - (8 * self.game.deltaTime) * (item.parentEntity.position[0] - (roundedPosition[0]))

        if(self.MinDistanceToConsumer(item) <= 8):
            currentScene.DeleteEntity(item.parentEntity)

    def OnEnable(self, currentScene: Scene):
        self.objectLayer = currentScene.tileMapLayersByName["Objects"].GetComponent(TilemapRenderer)

    def OnNewComponent(self, component: Component):  # Called when a new component is created into the scene. (Used to initialize that component)
        if(isinstance(component,ConsumerComponent)):
            self.consumers.append(component)

    def OnDestroyComponent(self, component: Component):  # Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        if(isinstance(component,ConsumerComponent)):
            self.consumers.remove(component)

    def MinDistanceToConsumer(self,item):
        minDistance = 999999
        consumer : ConsumerComponent
        for consumer in self.consumers:
            d = Distance(item.parentEntity.position,consumer.parentEntity.position)
            if(d < minDistance):
                minDistance = d
        return minDistance
