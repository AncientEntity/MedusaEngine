from engine.ecs import Component
from game.components.ItemComponent import ItemComponent


class GunComponent(ItemComponent):
    def __init__(self):
        super().__init__()
        self.bulletPrefabFunc = None # Func(currentScene)
        self.shootDelay = 0.01
        self.reloadTime = 0.8

        self.magazineCount = 99999999 # 10
        self.ammoReserves = 80

        self.activeMagazineCount = self.magazineCount
        self.lastShootTime = 0