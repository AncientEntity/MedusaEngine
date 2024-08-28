from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.ecs import Scene, Entity
from game import assets

class UIAmmoPrefabHandler:
    def __init__(self, gun):
        self.gun = gun

        self.ammoTop = None
        self.ammoBottom = None
        self.ammoMiddle = []
    def Delete(self, currentScene : Scene):
        if self.ammoTop:
            currentScene.DeleteEntity(self.ammoTop)

        if self.ammoBottom:
            currentScene.DeleteEntity(self.ammoBottom)

        for ammo in self.ammoMiddle:
            currentScene.DeleteEntity(ammo)

        self.ammoTop = None
        self.ammoBottom = None
        self.ammoMiddle = []

    def Render(self, currentScene : Scene):
        #import random
        currentX = -120 #random.randint(-115,-110)
        currentY = 40 + (self.gun.ammoPerMagazine - self.gun.ammo)*5

        if not self.ammoTop:
            topSpriteRenderer = SpriteRenderer(assets.uiTileset["ammo_top"])
            topSpriteRenderer.screenSpace = True
            self.ammoTop = currentScene.CreateEntity("UIAmmoTop", [currentX, currentY],
                                                     components=[topSpriteRenderer])
        else:
            self.ammoTop.position = [currentX, currentY]

        for i in range(self.gun.ammoPerMagazine):
            if i > self.gun.ammo-1:
                if self.ammoMiddle[i]:
                    self.ammoMiddle[i].position = [99999, 99999]
                continue

            currentY += 5
            if i >= len(self.ammoMiddle):
                spriteRenderer = SpriteRenderer(assets.uiTileset["ammo"])
                spriteRenderer.screenSpace = True
                self.ammoMiddle.append(currentScene.CreateEntity("UIAmmo", [currentX, currentY],
                                                                 components=[spriteRenderer]))
            else:
                self.ammoMiddle[i].position = [currentX, currentY]

        if not self.ammoBottom:
            botSpriteRenderer = SpriteRenderer(assets.uiTileset["ammo_bottom"])
            botSpriteRenderer.screenSpace = True
            self.ammoBottom = currentScene.CreateEntity("UIAmmoBottom", [currentX, currentY + 5],
                                                        components=[botSpriteRenderer])
        else:
            self.ammoBottom.position = [currentX, currentY + 5]