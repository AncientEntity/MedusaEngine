from engine.components.rendering.tilemaprenderer import Tilemap, TilemapRenderer
from engine.ecs import EntitySystem, Component, Scene
from engine.scenes.levelscene import LevelScene
from game.components.ItemComponent import ItemComponent
from game.constants import FirstConveyorSprite


class ItemSystem(EntitySystem):
    def __init__(self):
        super().__init__([ItemComponent])  # Put target components here
        self.objectLayer : TilemapRenderer = None
        self.conveyorSpeed = 35

    def Update(self, currentScene: LevelScene):
        item : ItemComponent
        for item in currentScene.components[ItemComponent]:
            roundedPosition = [item.parentEntity.position[0] // 16 * 16,item.parentEntity.position[1] // 16 * 16]
            itemTileIndex = self.objectLayer.GetTileIndexAtWorldPoint(roundedPosition[0],roundedPosition[1])
            if(itemTileIndex == None):
                continue
            overlappingTileId = self.objectLayer.tileMap.GetTileID(int(itemTileIndex[0]),int(itemTileIndex[1]))
            if(overlappingTileId != -1):
                self.HandleItem(item,overlappingTileId, roundedPosition)

    def HandleItem(self,item : ItemComponent,overlappingTileId : int, roundedPosition):
        targetX = False
        targetY = False
        if (overlappingTileId == FirstConveyorSprite):  # Move right
            item.parentEntity.position[0] += self.game.deltaTime * self.conveyorSpeed
            targetY = True
        elif (overlappingTileId == FirstConveyorSprite+1):  # Move down
            item.parentEntity.position[1] += self.game.deltaTime * self.conveyorSpeed
            targetX = True
        elif (overlappingTileId == FirstConveyorSprite+2):  # Move left
            item.parentEntity.position[0] -= self.game.deltaTime * self.conveyorSpeed
            targetY = True
        elif (overlappingTileId == FirstConveyorSprite+3):  # Move up
            item.parentEntity.position[1] -= self.game.deltaTime * self.conveyorSpeed
            targetX = True

        if(targetY):
            item.parentEntity.position[1] = item.parentEntity.position[1] - (8 * self.game.deltaTime) * (item.parentEntity.position[1] - (roundedPosition[1]))
        if(targetX):
            item.parentEntity.position[0] = item.parentEntity.position[0] - (8 * self.game.deltaTime) * (item.parentEntity.position[0] - (roundedPosition[0]+8))

    def OnEnable(self, currentScene: Scene):
        self.objectLayer = currentScene.tileMapLayersByName["Objects"].GetComponent(TilemapRenderer)

    def OnNewComponent(self, component: Component):  # Called when a new component is created into the scene. (Used to initialize that component)
        pass

    def OnDestroyComponent(self, component: Component):  # Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        pass
