from game import assets
from game.prefabs.ui.UIStatsBarPrefab import UIStatsBarPrefab


class UIHealthPrefabHandler(UIStatsBarPrefab):
    def __init__(self, actor):
        self.actor = actor

        super().__init__()

        self.minHealthShakePercent = 0.15

        self.lerpDelay = 0.01
        self.startingX = -120

        self.topSprite = assets.uiTileset["health_top"]
        self.bottomSprite = assets.uiTileset["health_bottom"]
        self.midSprites = []
        self.midSprites.append(assets.uiTileset["health_1"])
        self.midSprites.append(assets.uiTileset["health_2"])
        self.midSprites.append(assets.uiTileset["health_3"])
        self.midSprites.append(assets.uiTileset["health_4"])
        self.midSprites.append(assets.uiTileset["health_5"])
        self.midSprites.append(assets.uiTileset["health_6"])
        self.midSprites.append(assets.uiTileset["health_7"])
        self.midSprites.append(assets.uiTileset["health_8"])
        self.midEmptySprite = assets.uiTileset["health_empty"]
        self.margin = 1


    def GetValue(self) -> int:
        return self.actor.health // 4
    def GetValueMax(self) -> int:
        return self.actor.maxHealth // 4
    def GetShouldShake(self) -> bool:
        return self.actor.health / self.actor.maxHealth <= self.minHealthShakePercent