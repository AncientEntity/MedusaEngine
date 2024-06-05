import pygame

from engine.components.rendering.textrenderer import TextRenderer
from engine.ecs import EntitySystem, Scene


class UISystem(EntitySystem):
    def __init__(self):
        super().__init__()
    def OnEnable(self, currentScene : Scene):
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