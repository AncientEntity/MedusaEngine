from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.ecs import Scene, Entity
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

        self.xWhenGun = -95
        self.xWhenNoGun = -108
        self.startingY = 85

    def Render(self, currentScene : Scene):
        if not self.uiEntity:
            self.uiSpriteRenderer = SpriteRenderer(self.emptySprite,200,True)
            self.uiEntity = currentScene.CreateEntity("DashUI",[self.xWhenNoGun,self.startingY], components=[
                self.uiSpriteRenderer
            ])

        if time.time() - self.player.lastDashTime >= self.player.dashDelay:
            self.uiSpriteRenderer.sprite = self.fullSprite
        else:
            self.uiSpriteRenderer.sprite = self.emptySprite

        if self.actor.heldItem and self.actor.heldItem.GetComponent(GunComponent):
            self.uiEntity.position[0] = self.xWhenGun
        else:
            self.uiEntity.position[0] = self.xWhenNoGun


    def Delete(self, currentScene : Scene):
        if self.uiEntity:
            currentScene.DeleteEntity(self.uiEntity)
            self.uiEntity = None