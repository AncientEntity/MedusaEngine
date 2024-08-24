from engine.ecs import Component
from game.components.itemcomponent import ItemComponent


class GunComponent(ItemComponent):
    def __init__(self):
        super().__init__()
        self.bulletPrefabFunc = None # Func(currentScene)
        self.shootDelay = 0.4
        self.reloadTime = 1

        self.ammoPerMagazine = 10
        self.ammoReserves = 80
        self.ammo = self.ammoPerMagazine

        self.lastShootTime = 0

        self.friendly = True

        self.isReloading = False