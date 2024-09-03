from game import assets
from game.prefabs.ui.UIStatsBarPrefab import UIStatsBarPrefab


class UIXPrefabHandler(UIStatsBarPrefab):
    def __init__(self, actor):
        self.actor = actor

        super().__init__()

        self.lerpDelay = 0.01
        self.startingX = -125
        self.startingY = 90

        self.topSprite = assets.uiTileset["xp_left"]
        self.bottomSprite = assets.uiTileset["xp_right"]
        self.midSprites = [assets.uiTileset["xp_filled"]]
        self.midEmptySprite = assets.uiTileset["xp_empty"]
        self.margin = (-1,0)


    def GetValue(self) -> int:
        return self.actor.xp // 2
    def GetValueMax(self) -> int:
        return self.actor.xpPerLevel // 2