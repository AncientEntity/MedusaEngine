import pygame

from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.components.rendering.textrenderer import TextRenderer
from engine.components.rendering.tilemaprenderer import TilemapRenderer
from engine.components.ui.buttoncomponent import ButtonComponent
from engine.constants import CURSOR_PRESSED
from engine.ecs import EntitySystem
from engine.engine import Input
from engine.prefabs.ui.ButtonPrefab import CreateButtonPrefab
from engine.scenes.levelscene import LevelScene
from engine.systems.renderer import RenderingSystem
from game.constants import ConveyorPlaceable, UndergroundEntrance, UndergroundExit, worldSpriteSheet, \
    UNDERGROUND_BELT_UNLOCK_LEVEL
from game.datatypes.Placeable import Placeable
from game.prefabs.Generator import CreateGenerator
from game.systems.notificationsystem import NotificationSystem


class GameSystem(EntitySystem):
    def __init__(self):
        super().__init__()
        self._tileMapLayer : TilemapRenderer = None
        self._renderer : RenderingSystem = None
        self.previousHoverIndex = (0,0)
        self.placeRotation = 0
        self._money = 160

        self._level = 1
        self.levelDelay = 15
        self._levelTimeRemaining = self.levelDelay

        self.placeables = [ConveyorPlaceable,UndergroundEntrance,UndergroundExit]
        self.currentlyPlacing : Placeable = self.placeables[0]
    def OnEnable(self, currentScene : LevelScene):
        self.mainFont = pygame.font.Font("game/art/PixeloidMono-d94EV.ttf",10)

        self.moneyText = TextRenderer("$160",self.mainFont)
        self.levelText = TextRenderer("Level: 1",self.mainFont)
        self.nextOrderText = TextRenderer("Next Order: 20s",self.mainFont)

        self.moneyTextEnt = currentScene.CreateEntity("MoneyText",[-90,-128],components=[self.moneyText])
        self.moneyTextEnt.GetComponent(TextRenderer).SetColor((255,255,255))
        self.moneyTextEnt.GetComponent(TextRenderer).SetAntialiased(False)

        self.levelTextEnt = currentScene.CreateEntity("LevelText",[-30,-128],components=[self.levelText])
        self.levelTextEnt.GetComponent(TextRenderer).SetColor((255,255,255))
        self.levelTextEnt.GetComponent(TextRenderer).SetAntialiased(False)

        self.nextOrderTextEnt = currentScene.CreateEntity("NextOrderText",[65,-128],components=[self.nextOrderText])
        self.nextOrderTextEnt.GetComponent(TextRenderer).SetColor((255,255,255))
        self.nextOrderTextEnt.GetComponent(TextRenderer).SetAntialiased(False)

        self.placementPreviewRenderer = SpriteRenderer(worldSpriteSheet[ConveyorPlaceable.tiles[0]])
        self.placementPreviewIcon = currentScene.CreateEntity("PlacementPreviewIcon",[100,118],components=[self.placementPreviewRenderer])

        self.conveyorButton : ButtonComponent = CreateButtonPrefab(currentScene, worldSpriteSheet[(1,3)], "", self.mainFont).GetComponent(ButtonComponent)
        currentScene.AddComponent(SpriteRenderer(pygame.transform.scale(worldSpriteSheet[6],(8,8)),5,True),
                                  self.conveyorButton.parentEntity)
        self.conveyorButton.parentEntity.position = [-100,118]

        self._renderer = currentScene.GetSystemByClass(RenderingSystem)
        self._tileMapLayer = currentScene.tileMapLayersByName["Main"].GetComponent(TilemapRenderer)

    def Update(self, currentScene: LevelScene):
        self.WorldInteraction(currentScene)
        self.Controls()
        self.HandleRound(currentScene)

    def HandleRound(self,currentScene : LevelScene):
        self.SetLevelTimeRemaining(self._levelTimeRemaining - self.game.deltaTime)
        if(self._levelTimeRemaining <= 0):
            self._level += 1
            self.levelText.SetText("Level: "+str(self._level))
            self._levelTimeRemaining = self.levelDelay
            CreateGenerator(currentScene)
            if(self._level == UNDERGROUND_BELT_UNLOCK_LEVEL):
                self.UnlockUndergroundBelts(currentScene)


    def WorldInteraction(self, currentScene : LevelScene):
        currentHoverIndex = self._tileMapLayer.WorldPointToTileIndexSafe(self._renderer.worldMousePosition)
        if currentHoverIndex != None:
            currentScene.ClearTileLayer("HoverLayer")
            currentScene.SetTile(self.previousHoverIndex,"PreviewLayer",-1)
            self.previousHoverIndex = currentHoverIndex

            #Highlighting and Placing
            if(currentHoverIndex[0] >= 1 and currentHoverIndex[1] >= 1 and currentHoverIndex[0] <= 14 and currentHoverIndex[1] <= 14):
                # Handle special underground belt preview.
                if (self.currentlyPlacing == UndergroundEntrance):
                    self.UndergroundBeltPreview(currentHoverIndex, currentScene, False)
                elif (self.currentlyPlacing == UndergroundExit):
                    self.UndergroundBeltPreview(currentHoverIndex, currentScene, True)

                if(Input.MouseButtonPressed(0)):
                    currentScene.SetTile(currentHoverIndex,"HoverLayer",10)

                    #Attempt place
                    if(currentScene.GetTile(currentHoverIndex,"Objects") == -1 and self._money >= self.currentlyPlacing.cost):
                        self.AddMoney(-self.currentlyPlacing.cost)
                        currentScene.SetTile(currentHoverIndex,"Objects",self.GetPlacingTileIndex())
                elif(Input.MouseButtonPressed(2)):
                    currentScene.SetTile(currentHoverIndex,"HoverLayer",10)
                    if (currentScene.GetTile(currentHoverIndex, "Objects") != -1):
                        currentScene.SetTile(currentHoverIndex,"Objects",-1)
                else:
                    currentScene.SetTile(currentHoverIndex,"HoverLayer",9)
                    currentScene.SetTile(currentHoverIndex,"PreviewLayer", self.GetPlacingTileIndex())

    def Controls(self):
        if(Input.KeyDown(pygame.K_r)):
            self.placeRotation += 1
            self.placementPreviewRenderer.sprite = worldSpriteSheet[self.GetPlacingTileIndex()]
        if(Input.KeyDown(pygame.K_1) or self.conveyorButton.cursorState == CURSOR_PRESSED):
            self.currentlyPlacing = self.placeables[0]
            self.placementPreviewRenderer.sprite = worldSpriteSheet[self.GetPlacingTileIndex()]
        elif(self._level >= UNDERGROUND_BELT_UNLOCK_LEVEL and (Input.KeyDown(pygame.K_2) or self.undergroundEntranceButton.cursorState == CURSOR_PRESSED)):
            self.currentlyPlacing = self.placeables[1]
            self.placementPreviewRenderer.sprite = worldSpriteSheet[self.GetPlacingTileIndex()]
        elif(self._level >= UNDERGROUND_BELT_UNLOCK_LEVEL and (Input.KeyDown(pygame.K_3) or self.undergroundExitButton.cursorState == CURSOR_PRESSED)):
            self.currentlyPlacing = self.placeables[2]
            self.placementPreviewRenderer.sprite = worldSpriteSheet[self.GetPlacingTileIndex()]


    def AddMoney(self,moneyToAdd):
        self._money += moneyToAdd
        self.moneyText.SetText("$"+str(self._money))
    def SetLevelTimeRemaining(self,levelTime):
        self._levelTimeRemaining = levelTime
        self.nextOrderText.SetText("Next Order: "+str(int(self._levelTimeRemaining))+"s")

    def GetPlacingTileIndex(self):
        return self.currentlyPlacing.tiles[self.placeRotation % len(self.currentlyPlacing.tiles)]
    def UndergroundBeltPreview(self,hoverPos,currentScene : LevelScene, reverse):
        lookDirection = (0,0)
        if (self.GetPlacingTileIndex() == UndergroundEntrance.tiles[0] or self.GetPlacingTileIndex() == UndergroundExit.tiles[0]):  # move right
            lookDirection = (1, 0)
        elif(self.GetPlacingTileIndex() == UndergroundEntrance.tiles[1] or self.GetPlacingTileIndex() == UndergroundExit.tiles[1]): #move down
            lookDirection = (0,1)
        elif(self.GetPlacingTileIndex() == UndergroundEntrance.tiles[2] or self.GetPlacingTileIndex() == UndergroundExit.tiles[2]): #move left
            lookDirection = (-1,0)
        elif(self.GetPlacingTileIndex() == UndergroundEntrance.tiles[3] or self.GetPlacingTileIndex() == UndergroundExit.tiles[3]): #move up
            lookDirection = (0,-1)

        if(reverse):
            lookDirection = (-lookDirection[0],-lookDirection[1])

        position = list(hoverPos)
        for i in range(3):
            position[0] += lookDirection[0]
            position[1] += lookDirection[1]
            if(position[0] < 1 or position[0] > 14):
                return
            if(position[1] < 1 or position[1] > 14):
                return
            currentScene.SetTile(position, "HoverLayer", 9, True)
    def UnlockUndergroundBelts(self, currentScene): # I don't like this solution but for a remake/example game it's not an issue.

        self.undergroundEntranceButton : ButtonComponent = CreateButtonPrefab(currentScene, worldSpriteSheet[(1,3)], "", self.mainFont).GetComponent(ButtonComponent)
        currentScene.AddComponent(SpriteRenderer(pygame.transform.scale(worldSpriteSheet[2], (8, 8)), 5,True),
                                  self.undergroundEntranceButton.parentEntity)
        self.undergroundEntranceButton.parentEntity.position = [-80,118]

        self.undergroundExitButton : ButtonComponent = CreateButtonPrefab(currentScene, worldSpriteSheet[(1,3)], "", self.mainFont).GetComponent(ButtonComponent)
        currentScene.AddComponent(SpriteRenderer(pygame.transform.scale(worldSpriteSheet[3], (8, 8)), 5,True),
                                  self.undergroundExitButton.parentEntity)
        self.undergroundExitButton.parentEntity.position = [-60,118]

        currentScene.GetSystemByClass(NotificationSystem).CreateNotification(currentScene, "Underground Belts Unlocked!")