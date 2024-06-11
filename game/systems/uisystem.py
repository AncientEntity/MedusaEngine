import pygame

from engine.components.rendering.textrenderer import TextRenderer
from engine.components.rendering.tilemaprenderer import TilemapRenderer
from engine.ecs import EntitySystem, Scene
from engine.engine import Input
from engine.scenes.levelscene import LevelScene
from engine.systems import renderer
from engine.systems.renderer import RenderingSystem


class UISystem(EntitySystem):
    def __init__(self):
        super().__init__()
        self._tileMapLayer : TilemapRenderer = None
        self._renderer : RenderingSystem = None
        self.previousHoverIndex = (0,0)
    def OnEnable(self, currentScene : LevelScene):
        self.mainFont = pygame.font.Font("game\\art\\PixeloidMono-d94EV.ttf",10)

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
        currentHoverIndex = self._tileMapLayer.GetTileIndexAtWorldPoint(self._renderer.worldMousePosition[0], self._renderer.worldMousePosition[1])
        if currentHoverIndex != None:
            currentScene.SetTile(self.previousHoverIndex[0], self.previousHoverIndex[1], "HoverLayer", -1)
            self.previousHoverIndex = currentHoverIndex
            if(Input.MouseButtonPressed(0)):
                currentScene.SetTile(self.previousHoverIndex[0],self.previousHoverIndex[1],"HoverLayer",6)
            else:
                currentScene.SetTile(self.previousHoverIndex[0],self.previousHoverIndex[1],"HoverLayer",5)
