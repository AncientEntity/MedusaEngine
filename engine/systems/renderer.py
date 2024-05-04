import math

import pygame.display

from engine.components.rendering.renderercomponent import RendererComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.components.rendering.tilemaprenderer import TilemapRenderer
from engine.datatypes.sprites import GetSprite
from engine.ecs import EntitySystem, Scene, Component
from engine.logging import Log, LOG_ALL


def CenterToTopLeftPosition(centerPosition, surface : pygame.Surface):
    return [centerPosition[0]-surface.get_width()//2,centerPosition[1]-surface.get_height()//2]

class RenderingSystem(EntitySystem):
    instance = None
    def __init__(self):
        super().__init__([SpriteRenderer,TilemapRenderer])
        self.cameraPosition = [0,0]
        self.renderScale = 3
        self.backgroundColor = (255,255,255)
        self._renderTarget = None
        self._screenSize = None
        self._scaledScreenSize = None
        self._scaledHalfSize = None
        self.debug = False

        self._sortedRenderOrder : list = [] #Sorted list of related components (ie SpriteRenderer). Sorted by sort order.

    def OnEnable(self):
        RenderingSystem.instance = self
        self._screenSize = [self.game.display.get_width(),self.game.display.get_height()]
        self._scaledScreenSize = [self.game.display.get_width() // self.renderScale,self.game.display.get_height() // self.renderScale]
        self._scaledHalfSize = [self._scaledScreenSize[0]//2,self._scaledScreenSize[1]//2]
        self._renderTarget = pygame.Surface(self._scaledScreenSize)

    def OnNewComponent(self,component : Component):
        self.InsertIntoSortedRenderOrder(component)
        Log("Added "+component.parentEntity.name + " to rendering order."+str(component.drawOrder),LOG_ALL)

    def OnDestroyComponent(self, component : Component):
        indexOfComponent = self._sortedRenderOrder.index(component)
        if(indexOfComponent != -1):
            self._sortedRenderOrder.pop(indexOfComponent)
            Log("Removed "+component.parentEntity.name+" from rendering order.",LOG_ALL)

    def InsertIntoSortedRenderOrder(self,component : RendererComponent):
        # If _sortedRenderOrder is empty, just simply add and exit.
        if(len(self._sortedRenderOrder) == 0):
            self._sortedRenderOrder.append(component)
            return

        #Otherwise sort component into _sortedRenderOrder with basic insertion sort.

        existingComponent : RendererComponent = self._sortedRenderOrder[0]
        i = 0
        while(existingComponent.drawOrder < component.drawOrder):
            i += 1
            if(i == len(self._sortedRenderOrder)):
                self._sortedRenderOrder.append(component)
                return
            existingComponent = self._sortedRenderOrder[i]
        self._sortedRenderOrder.insert(i,component)

    def Update(self,currentScene : Scene):
        self._renderTarget.fill(self.backgroundColor)
        self.cameraPosition = [math.floor(self.cameraPosition[0]),math.floor(self.cameraPosition[1])]

        #Loop through sorted render order and render everything out.
        for renderer in self._sortedRenderOrder:
            if(isinstance(renderer,SpriteRenderer)):
                self.RenderSpriteRenderer(renderer)
            elif(isinstance(renderer,TilemapRenderer)):
                self.RenderTileMapRenderer(renderer)

        #Finally blit the render target onto the final display.
        self.game.display.blit(pygame.transform.scale(self._renderTarget,(self._screenSize[0],self._screenSize[1])),(0,0))
        pygame.display.update()

    def RenderSpriteRenderer(self,spriteRenderer : SpriteRenderer):
        if (spriteRenderer.sprite == None):
            return

        actualSprite = GetSprite(spriteRenderer.sprite)
        # Validate if we found an actual sprite
        if (actualSprite == None):
            return

        # Verify what is being drawn is on the screen
        if (False == self.IsOnScreenSprite(actualSprite, spriteRenderer.parentEntity.position)):
            return

        finalPosition = self.FinalPositionOfSprite(spriteRenderer.parentEntity.position, actualSprite)
        self._renderTarget.blit(actualSprite, finalPosition)

        if (self.debug):  # If debug draw bounds of spriterenderers
            pygame.draw.rect(self._renderTarget, (255, 0, 0),
                             pygame.Rect(finalPosition[0] - 1, finalPosition[1], actualSprite.get_width(),
                                         actualSprite.get_height()), width=1)

    def RenderTileMapRenderer(self,tileMapRenderer : TilemapRenderer):
        if (tileMapRenderer.tileMap == None or tileMapRenderer.tileMap.tileSet == None):
            return
        centeredOffset = [tileMapRenderer.parentEntity.position[0] - (
                    tileMapRenderer.tileMap.size[0] * tileMapRenderer.tileMap.tileSize) // 2,
                          tileMapRenderer.parentEntity.position[1] - (
                                      tileMapRenderer.tileMap.size[1] * tileMapRenderer.tileMap.tileSize) // 2]
        for x in range(tileMapRenderer.tileMap.size[0]):
            for y in range(tileMapRenderer.tileMap.size[1]):
                if (tileMapRenderer.tileMap.map[x][y] == -1):  # Empty tile
                    continue

                # Get world position then the left anchored screen position
                worldPosition = [centeredOffset[0] + (x * tileMapRenderer.tileMap.tileSize),
                                 centeredOffset[1] + (y * tileMapRenderer.tileMap.tileSize)]
                leftAnchoredScreenPosition = self.WorldToScreenPosition(worldPosition)

                if (False == self.IsOnScreenRect(
                        pygame.Rect(worldPosition[0], worldPosition[1], tileMapRenderer.tileMap.tileSize,
                                    tileMapRenderer.tileMap.tileSize))):
                    continue

                targetSprite = GetSprite(tileMapRenderer.tileMap.tileSet[tileMapRenderer.tileMap.map[x][y]])
                self._renderTarget.blit(targetSprite, leftAnchoredScreenPosition)

    def WorldToScreenPosition(self,position):
        return [position[0] - self.cameraPosition[0] + self._scaledHalfSize[0], position[1] - self.cameraPosition[1] + self._scaledHalfSize[1]]

    def FinalPositionOfSprite(self,position,sprite):
        topLeftPosition = CenterToTopLeftPosition(position, sprite)
        return self.WorldToScreenPosition(topLeftPosition)

    def IsOnScreenSprite(self, sprite : pygame.Surface, position) -> bool:
        return self.IsOnScreenRect(pygame.Rect(position[0]-sprite.get_width()//2,position[1]-sprite.get_height()//2,sprite.get_width(),sprite.get_height()))

    def IsOnScreenRect(self,rect : pygame.Rect):
        screenBounds = pygame.Rect(self.cameraPosition[0] - self._scaledHalfSize[0],self.cameraPosition[1] - self._scaledHalfSize[1],self._scaledScreenSize[0],self._scaledScreenSize[1])
        return screenBounds.colliderect(rect)

    def DebugDrawWorldRect(self,color,rect):
        worldP = self.WorldToScreenPosition((rect.x,rect.y))
        pygame.draw.rect(self._renderTarget,(255,0,0),(worldP[0],worldP[1],rect.w,rect.h))