from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.ecs import Scene
import time
import random

class UIStatsBarPrefab:
    def __init__(self):

        self.topSprite = None
        self.midSprites = []
        self.midEmptySprite = None
        self.bottomSprite = None
        self.drawOrder = 200

        self.startingX = -120
        self.startingY = 90

        self.statsTop = None
        self.statsBottom = None
        self.statsMiddle = []

        self.valueLerp = self.GetValue()
        self.lastLerpChange = 0
        self.lerpDelay = 0.02

        self.margin = 5

    def Delete(self, currentScene : Scene):
        if self.statsTop:
            currentScene.DeleteEntity(self.statsTop)

        if self.statsBottom:
            currentScene.DeleteEntity(self.statsBottom)

        for ammo in self.statsMiddle:
            currentScene.DeleteEntity(ammo)

        self.statsTop = None
        self.statsBottom = None
        self.statsMiddle = []

    def Render(self, currentScene : Scene):
        currentX = self.startingX
        currentY = self.startingY

        if self.GetShouldShake():
            currentX += random.randint(-1,1)
            currentY += random.randint(-1,1)

        if not self.statsBottom:
            # If statsBottom doesn't exist it is the first time, therefore force value lerp
            self.valueLerp = self.GetValue()

            botSpriteRenderer = SpriteRenderer(self.bottomSprite)
            botSpriteRenderer.screenSpace = True
            botSpriteRenderer.drawOrder = self.drawOrder
            self.statsBottom = currentScene.CreateEntity("UIStatBottom", [currentX, currentY],
                                                         components=[botSpriteRenderer])
        else:
            self.statsBottom.position = [currentX, currentY]

        self.LerpValue()

        for i in range(self.GetValueMax()):
            if i > self.valueLerp-1:
                if i < len(self.statsMiddle):
                    if not self.midEmptySprite:
                        self.statsMiddle[i].position = [99999, 99999]
                        continue
                    else:
                        self.statsMiddle[i].GetComponent(SpriteRenderer).sprite = self.midEmptySprite

            currentY -= self.margin
            if i >= len(self.statsMiddle):
                spriteRenderer = SpriteRenderer(self.midSprites[random.randint(0,len(self.midSprites)-1)])
                spriteRenderer.screenSpace = True
                spriteRenderer.drawOrder = self.drawOrder
                self.statsMiddle.append(currentScene.CreateEntity("UIStatCenter", [currentX, currentY],
                                                                  components=[spriteRenderer]))
            else:
                self.statsMiddle[i].position = [currentX, currentY]

        if not self.statsTop:
            topSpriteRenderer = SpriteRenderer(self.topSprite)
            topSpriteRenderer.screenSpace = True
            topSpriteRenderer.drawOrder = self.drawOrder
            self.statsTop = currentScene.CreateEntity("UIStatTop", [currentX, currentY - self.margin],
                                                      components=[topSpriteRenderer])
        else:
            self.statsTop.position = [currentX, currentY - self.margin]


    def LerpValue(self):
        if self.valueLerp == self.GetValue():
            return
        if not self.lerpDelay:
            self.valueLerp = self.GetValue()
            return

        lastLerpTime = time.time() - self.lastLerpChange

        if lastLerpTime >= self.lerpDelay:
            if self.valueLerp < self.GetValue():
                self.valueLerp += 1
            else:
                self.valueLerp -= 1
            self.lastLerpChange = time.time()

    def GetValue(self) -> int:
        return 0
    def GetValueMax(self) -> int:
        return 10

    def GetShouldShake(self) -> bool:
        return False