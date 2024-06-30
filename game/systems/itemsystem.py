from engine.components.physicscomponent import PhysicsComponent
from engine.components.rendering.tilemaprenderer import TilemapRenderer
from engine.ecs import EntitySystem, Component, Scene
from engine.scenes.levelscene import LevelScene
from engine.tools.math import Distance
from game.components.ConsumerComponent import ConsumerComponent
from game.components.ItemComponent import ItemComponent
from game.constants import ConveyorPlaceable, UndergroundExit, UndergroundEntrance
import time

from game.systems.gamesystem import GameSystem


class ItemSystem(EntitySystem):
    def __init__(self):
        super().__init__([ItemComponent,ConsumerComponent])  # Put target components here
        self.objectLayer : TilemapRenderer = None
        self.conveyorSpeed = 35

        self.consumers = []

        self._blockedUndergroundExits = []

    def Update(self, currentScene: LevelScene):
        self._blockedUndergroundExits.clear()

        item : ItemComponent
        for item in currentScene.components[ItemComponent]:
            self.HandleItem(item, currentScene)

    def HandleItem(self,item : ItemComponent, currentScene : LevelScene):

        #Handle underground belt reappear
        if(item.reappearTime != None):
            reappearIndex = self.objectLayer.WorldPositionToTileIndex(item.reappearPosition)
            if(item.reappearTime > time.time()):
                return
            elif reappearIndex != None and tuple(reappearIndex) not in self._blockedUndergroundExits:
                item.reappearTime = None
                item.parentEntity.position = item.reappearPosition
                item.reappearPosition = None
            else:
                return

        #Calculate movement related variables
        itemTileIndex = self.objectLayer.WorldPointToTileIndexSafe(
            (item.parentEntity.position[0], item.parentEntity.position[1]))


        if (itemTileIndex == None):
            return
        overlappingTileId = self.objectLayer.tileMap.GetTileID(int(itemTileIndex[0]), int(itemTileIndex[1]))
        if (overlappingTileId == -1):
            return

        if(overlappingTileId in UndergroundExit.tiles):
            self._blockedUndergroundExits.append(tuple(itemTileIndex))

        roundedPosition = self.objectLayer.TileIndexToWorldPosition(itemTileIndex,True)

        self.ConveyorMove(item,overlappingTileId,roundedPosition)

        nearbyConsumer = self.GetNearbyConsumer(item)
        if(nearbyConsumer):
            currentScene.DeleteEntity(item.parentEntity)
            if(nearbyConsumer.itemID == item.itemID):
                currentScene.GetSystemByClass(GameSystem).AddMoney(item.worth)
            else:
                currentScene.GetSystemByClass(GameSystem).AddMoney(-1)

        self.UndergroundEntranceMove(item,overlappingTileId)

    def UndergroundEntranceMove(self,item : ItemComponent,overlappingTileId):
        lookDirection = (0,0)

        if (overlappingTileId == UndergroundEntrance.tiles[0]):  # move right
            lookDirection = (1, 0)
        elif(overlappingTileId == UndergroundEntrance.tiles[1]): #move down
            lookDirection = (0,1)
        elif(overlappingTileId == UndergroundEntrance.tiles[2]): #move left
            lookDirection = (-1,0)
        elif(overlappingTileId == UndergroundEntrance.tiles[3]): #move up
            lookDirection = (0,-1)

        if(lookDirection == (0,0)):
            return

        curLookPos = list(self.objectLayer.WorldPositionToTileIndex(item.parentEntity.position))
        targetExitPosition = None
        for i in range(3):
            curLookPos[0] += lookDirection[0]
            curLookPos[1] += lookDirection[1]
            curLookID = self.objectLayer.tileMap.GetTileID(curLookPos[0],curLookPos[1])
            if(overlappingTileId == UndergroundEntrance.tiles[0] and curLookID == UndergroundExit.tiles[0]): #move right
                targetExitPosition = self.objectLayer.TileIndexToWorldPosition(curLookPos,True)
            elif(overlappingTileId == UndergroundEntrance.tiles[1] and curLookID == UndergroundExit.tiles[1]): #move right
                targetExitPosition = self.objectLayer.TileIndexToWorldPosition(curLookPos,True)
            elif(overlappingTileId == UndergroundEntrance.tiles[2] and curLookID == UndergroundExit.tiles[2]): #move right
                targetExitPosition = self.objectLayer.TileIndexToWorldPosition(curLookPos,True)
            elif(overlappingTileId == UndergroundEntrance.tiles[3] and curLookID == UndergroundExit.tiles[3]): #move right
                targetExitPosition = self.objectLayer.TileIndexToWorldPosition(curLookPos,True)
            if(targetExitPosition != None):
                break

        if(targetExitPosition == None):
            return
        if(tuple(curLookPos) in self._blockedUndergroundExits): #make sure underground exit wont be blocked
            return

        #Found an exit position, handle it.
        item.reappearPosition = targetExitPosition
        item.reappearTime = time.time() + (i+1)*0.5
        item.parentEntity.position[0] += 9999       # for now move it way off-screen.


    def ConveyorMove(self,item,overlappingTileId,roundedPosition):
        targetX = False
        targetY = False
        finalMoveAmount = [0,0]
        if (overlappingTileId == ConveyorPlaceable.tiles[0] or overlappingTileId == UndergroundExit.tiles[0]):  # Move right
            finalMoveAmount[0] += self.game.deltaTime * self.conveyorSpeed
            targetY = True
        elif (overlappingTileId == ConveyorPlaceable.tiles[1] or overlappingTileId == UndergroundExit.tiles[1]):  # Move down
            finalMoveAmount[1] += self.game.deltaTime * self.conveyorSpeed
            targetX = True
        elif (overlappingTileId == ConveyorPlaceable.tiles[2] or overlappingTileId == UndergroundExit.tiles[2]):  # Move left
            finalMoveAmount[0] -= self.game.deltaTime * self.conveyorSpeed
            targetY = True
        elif (overlappingTileId == ConveyorPlaceable.tiles[3] or overlappingTileId == UndergroundExit.tiles[3]):  # Move up
            finalMoveAmount[1] -= self.game.deltaTime * self.conveyorSpeed
            targetX = True

        if(targetY):
            finalMoveAmount[1]  -= (8 * self.game.deltaTime) * (item.parentEntity.position[1] - (roundedPosition[1]))
        if(targetX):
            finalMoveAmount[0] -= (8 * self.game.deltaTime) * (item.parentEntity.position[0] - (roundedPosition[0]))

        if(not item._physics):
            item._physics = item.parentEntity.GetComponent(PhysicsComponent)
        item._physics.Move(finalMoveAmount)

    def OnEnable(self, currentScene: Scene):
        self.objectLayer = currentScene.tileMapLayersByName["Objects"]

    def OnNewComponent(self, component: Component):  # Called when a new component is created into the scene. (Used to initialize that component)
        if(isinstance(component,ConsumerComponent)):
            self.consumers.append(component)

    def OnDeleteComponent(self, component: Component):  # Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        if(isinstance(component,ConsumerComponent)):
            self.consumers.remove(component)

    def GetNearbyConsumer(self,item):
        minDistance = 10
        nearest = None
        consumer : ConsumerComponent
        for consumer in self.consumers:
            d = Distance(item.parentEntity.position,consumer.parentEntity.position)
            if(d < minDistance):
                minDistance = d
                nearest = consumer
        return nearest
