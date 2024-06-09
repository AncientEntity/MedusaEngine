import pygame

from engine.components.rendering.textrenderer import TextRenderer
from engine.components.rendering.tilemaprenderer import TilemapRenderer
from engine.ecs import EntitySystem, Scene
from engine.scenes.levelscene import LevelScene
from engine.systems import renderer
from engine.systems.renderer import RenderingSystem


class UISystem(EntitySystem):
    def __init__(self):
        super().__init__()
        self._tileMapLayer : TilemapRenderer = None
        self._renderer : RenderingSystem = None
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
        self._tileMapLayer = currentScene.tileMapLayersByName["Tile Layer 1"].GetComponent(TilemapRenderer)

    def Update(self, currentScene: Scene):
        tileIndex = self._tileMapLayer.GetTileIndexAtPoint(self._renderer.worldMousePosition[0],self._renderer.worldMousePosition[1])
        #print(tileIndex)