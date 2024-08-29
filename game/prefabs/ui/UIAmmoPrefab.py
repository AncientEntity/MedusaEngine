from game import assets
from game.prefabs.ui.UIStatsBarPrefab import UIStatsBarPrefab


class UIAmmoPrefabHandler(UIStatsBarPrefab):
    def __init__(self, gun):
        self.gun = gun

        super().__init__()

        self.startingX = -108

        self.topSprite = assets.uiTileset["ammo_top"]
        self.midSprites = [ assets.uiTileset["ammo"]]
        self.midEmptySprite = None
        self.bottomSprite = assets.uiTileset["ammo_bottom"]


    def GetValue(self) -> int:
        return self.gun.ammo
    def GetValueMax(self) -> int:
        return self.gun.ammoPerMagazine
    def GetShouldShake(self) -> bool:
        return self.gun.isReloading