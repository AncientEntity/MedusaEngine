import pygame

from engine.components.rendering.textrenderer import TextRenderer
from engine.components.rendering.tilemaprenderer import TilemapRenderer
from engine.ecs import EntitySystem
from engine.engine import Input
from engine.scenes.levelscene import LevelScene
from engine.systems.renderer import RenderingSystem
from game.constants import ConveyorPlaceable, UndergroundEntrance, UndergroundExit
from game.datatypes.Placeable import Placeable
from game.prefabs.Generator import CreateGenerator


class GameSystem(EntitySystem):
    def __init__(self):
        super().__init__()
        self._tileMapLayer : TilemapRenderer = None
        self._renderer : RenderingSystem = None
        self.previousHoverIndex = (0,0)
        self.placeRotation = 0
        self._money = 1000

        self._level = 1
        self.levelDelay = 5
        self._levelTimeRemaining = self.levelDelay

        self.placeables = [ConveyorPlaceable,UndergroundEntrance,UndergroundExit]
        self.currentlyPlacing : Placeable = self.placeables[0]
    def OnEnable(self, currentScene : LevelScene):
        self.mainFont = pygame.font.Font("game/art/PixeloidMono-d94EV.ttf",10)

        self.moneyText = TextRenderer("$1000",self.mainFont)
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


    def WorldInteraction(self, currentScene : LevelScene):
        currentHoverIndex = self._tileMapLayer.WorldPointToTileIndexSafe(self._renderer.worldMousePosition)
        print(currentHoverIndex)
        if currentHoverIndex != None:
            currentScene.SetTile(self.previousHoverIndex, "HoverLayer", -1)
            currentScene.SetTile(self.previousHoverIndex,"PreviewLayer",-1)
            self.previousHoverIndex = currentHoverIndex

            #Highlighting and Placing
            if(currentHoverIndex[0] >= 1 and currentHoverIndex[1] >= 1 and currentHoverIndex[0] <= 14 and currentHoverIndex[1] <= 14):
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
        if(Input.KeyDown(pygame.K_1)):
            self.currentlyPlacing = self.placeables[0]
        elif(Input.KeyDown(pygame.K_2)):
            self.currentlyPlacing = self.placeables[1]
        elif(Input.KeyDown(pygame.K_3)):
            self.currentlyPlacing = self.placeables[2]

    def AddMoney(self,moneyToAdd):
        self._money += moneyToAdd
        self.moneyText.SetText("$"+str(self._money))
    def SetLevelTimeRemaining(self,levelTime):
        self._levelTimeRemaining = levelTime
        self.nextOrderText.SetText("Next Order: "+str(int(self._levelTimeRemaining))+"s")

    def GetPlacingTileIndex(self):
        return self.currentlyPlacing.tiles[self.placeRotation % len(self.currentlyPlacing.tiles)]