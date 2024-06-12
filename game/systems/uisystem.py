import pygame

from engine.components.rendering.textrenderer import TextRenderer
from engine.components.rendering.tilemaprenderer import TilemapRenderer
from engine.ecs import EntitySystem, Scene
from engine.engine import Input
from engine.scenes.levelscene import LevelScene
from engine.systems import renderer
from engine.systems.renderer import RenderingSystem

CONVEYORSPRITE = 4


class UISystem(EntitySystem):
    def __init__(self):
        super().__init__()
        self._tileMapLayer : TilemapRenderer = None
        self._renderer : RenderingSystem = None
        self.previousHoverIndex = (0,0)
        self.placeRotation = 0
    def OnEnable(self, currentScene : LevelScene):
        self.mainFont = pygame.font.Font("game/art/PixeloidMono-d94EV.ttf",10)

        self.moneyText = currentScene.CreateEntity("MoneyText",[-90,-128],components=[TextRenderer("$1000",self.mainFont)])
        self.moneyText.GetComponent(TextRenderer).SetColor((255,255,255))
        self.moneyText.GetComponent(TextRenderer).SetAntialiased(False)

        self.levelText = currentScene.CreateEntity("LevelText",[-30,-128],components=[TextRenderer("Level: 15",self.mainFont)])
        self.levelText.GetComponent(TextRenderer).SetColor((255,255,255))
        self.levelText.GetComponent(TextRenderer).SetAntialiased(False)

        self.nextOrderText = currentScene.CreateEntity("NextOrderText",[65,-128],components=[TextRenderer("Next Order: 12s",self.mainFont)])
        self.nextOrderText.GetComponent(TextRenderer).SetColor((255,255,255))
        self.nextOrderText.GetComponent(TextRenderer).SetAntialiased(False)

        self._renderer = currentScene.GetSystemByClass(RenderingSystem)
        self._tileMapLayer = currentScene.tileMapLayersByName["Main"].GetComponent(TilemapRenderer)

    def Update(self, currentScene: LevelScene):
        self.WorldInteraction(currentScene)
    def WorldInteraction(self, currentScene : LevelScene):
        currentHoverIndex = self._tileMapLayer.GetTileIndexAtWorldPoint(self._renderer.worldMousePosition[0], self._renderer.worldMousePosition[1])
        if currentHoverIndex != None:
            currentScene.SetTile(self.previousHoverIndex, "HoverLayer", -1)
            currentScene.SetTile(self.previousHoverIndex,"PreviewLayer",-1)
            self.previousHoverIndex = currentHoverIndex

            if(currentHoverIndex[0] >= 1 and currentHoverIndex[1] >= 1 and currentHoverIndex[0] <= 14 and currentHoverIndex[1] <= 14):
                if(Input.MouseButtonPressed(0)):
                    currentScene.SetTile(currentHoverIndex,"HoverLayer",10)
                    currentScene.SetTile(currentHoverIndex,"Objects",CONVEYORSPRITE+self.placeRotation % 4)
                else:
                    currentScene.SetTile(currentHoverIndex,"HoverLayer",9)
                    currentScene.SetTile(currentHoverIndex,"PreviewLayer",CONVEYORSPRITE+self.placeRotation % 4)

        if(Input.KeyDown(pygame.K_r)):
            self.placeRotation += 1