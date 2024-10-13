from engine.components.recttransformcomponent import RectTransformComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.constants import ALIGN_BOTTOMLEFT
from engine.ecs import Scene, Entity
from engine.systems.ui import UISystem
from game import assets
from game.components.guncomponent import GunComponent
from game.prefabs.ui.UIBasePrefab import UIBasePrefab
import time

class UIDashPrefab(UIBasePrefab):
    def __init__(self, player, actor):
        self.fullSprite = assets.uiTileset["dash_full"]
        self.emptySprite = assets.uiTileset["dash_empty"]

        self.player = player
        self.actor = actor

        self.uiEntity : Entity = None
        self.uiSpriteRenderer : SpriteRenderer = None

        self.xWhenGun = 32
        self.xWhenNoGun = 16
        self.startingY = 78

        self.uiContainer = None
        self.transform = None

    def Render(self, currentScene : Scene):
        if not self.uiContainer:
            self.uiContainer = currentScene.GetSystemByClass(UISystem).GetRectTransformByName("UI-StatsContainer")
        if not self.uiContainer:
            return

        if not self.uiEntity:
            self.uiSpriteRenderer = SpriteRenderer(self.emptySprite,1500,True)
            self.transform = RectTransformComponent(ALIGN_BOTTOMLEFT, (self.xWhenNoGun,-15),parent=self.uiContainer)
            self.uiEntity = currentScene.CreateEntity("DashUI",(0,0), components=[
                self.uiSpriteRenderer,
                self.transform,
            ])

        if time.time() - self.player.lastDashTime >= self.player.dashDelay:
            self.uiSpriteRenderer.sprite = self.fullSprite
        else:
            self.uiSpriteRenderer.sprite = self.emptySprite

        if self.actor.heldItem and self.actor.heldItem.GetComponent(GunComponent):
            self.transform.SetAnchorOffset((self.xWhenGun,-15))
            #self.uiEntity.position[0] = self.xWhenGun
        else:
            #self.uiEntity.position[0] = self.xWhenNoGun
            self.transform.SetAnchorOffset((self.xWhenNoGun,-15))


    def Delete(self, currentScene : Scene):
        if self.uiEntity:
            currentScene.DeleteEntity(self.uiEntity)
            self.uiEntity = None