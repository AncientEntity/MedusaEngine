import math

import pygame.display

from engine.components.rendering.particlecomponent import ParticleEmitterComponent, Particle
from engine.components.rendering.renderercomponent import RendererComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.components.rendering.textrenderer import TextRenderer
from engine.components.rendering.tilemaprenderer import TilemapRenderer
from engine.datatypes.sprites import GetSprite, Sprite
from engine.ecs import EntitySystem, Scene, Component
from engine.logging import Log, LOG_ALL


def CenterToTopLeftPosition(centerPosition, surface : pygame.Surface):
    return [centerPosition[0]-surface.get_width()//2,centerPosition[1]-surface.get_height()//2]

class RenderingSystem(EntitySystem):
    instance = None
    def __init__(self):
        super().__init__([SpriteRenderer,TilemapRenderer,ParticleEmitterComponent,TextRenderer])
        self.cameraPosition = [0,0]
        self.renderScale = 3
        self.backgroundColor = (255,255,255)
        self._renderTarget = None
        self._screenSize = None
        self._scaledScreenSize = None
        self._scaledHalfSize = None
        self.debug = False

        self._sortedDrawOrder : list = [] #Sorted list of related components (ie SpriteRenderer). Sorted by sort order.

        self.rawMousePosition = (0, 0)
        self.screenMousePosition = (0, 0)
        self.worldMousePosition = (0,0)

    def OnEnable(self, currentScene : Scene):
        RenderingSystem.instance = self
        self._screenSize = [self.game.display.get_width(),self.game.display.get_height()]
        self._scaledScreenSize = [self.game.display.get_width() / self.renderScale,self.game.display.get_height() / self.renderScale]
        self._scaledHalfSize = [self._scaledScreenSize[0]/2,self._scaledScreenSize[1]/2]
        self._renderTarget = pygame.Surface(self._scaledScreenSize)

    def OnNewComponent(self,component : RendererComponent):
        self.InsertIntoSortedRenderOrder(component)
        Log("Added "+component.parentEntity.name + " to rendering order."+str(component.drawOrder),LOG_ALL)

    def OnDestroyComponent(self, component : RendererComponent):
        indexOfComponent = self._sortedDrawOrder.index(component)
        if(indexOfComponent != -1):
            self._sortedDrawOrder.pop(indexOfComponent)
            Log("Removed "+component.parentEntity.name+" from rendering order.",LOG_ALL)

    def InsertIntoSortedRenderOrder(self,component : RendererComponent):
        # If _sortedRenderOrder is empty, just simply add and exit.
        if(len(self._sortedDrawOrder) == 0):
            self._sortedDrawOrder.append(component)
            return

        #Otherwise sort component into _sortedRenderOrder with basic insertion sort.

        existingComponent : RendererComponent = self._sortedDrawOrder[0]
        i = 0
        while(existingComponent.drawOrder < component.drawOrder):
            i += 1
            if(i == len(self._sortedDrawOrder)):
                self._sortedDrawOrder.append(component)
                return
            existingComponent = self._sortedDrawOrder[i]
        self._sortedDrawOrder.insert(i, component)

    def Update(self,currentScene : Scene):
        self._renderTarget.fill(self.backgroundColor)
        self.cameraPosition = [self.cameraPosition[0],self.cameraPosition[1]]

        self.rawMousePosition = pygame.mouse.get_pos()
        self.screenMousePosition = ((self.rawMousePosition[0] - self._screenSize[0] / 2) / self.renderScale,(self.rawMousePosition[1] - self._screenSize[1] / 2) / self.renderScale)
        self.worldMousePosition = (round((self.rawMousePosition[0] + self.cameraPosition[0] - self._screenSize[0] / 2) / self.renderScale),
                                   round((self.rawMousePosition[1] + self.cameraPosition[1] - self._screenSize[1] / 2) / self.renderScale))

        #Loop through sorted render order and render everything out.
        for component in self._sortedDrawOrder:
            if(isinstance(component,SpriteRenderer)):
                self.RenderSpriteRenderer(component)
            elif(isinstance(component,TilemapRenderer)):
                self.RenderTileMapRenderer(component)
            elif(isinstance(component,ParticleEmitterComponent)):
                self.RenderParticleEmitter(component)
            elif(isinstance(component, TextRenderer)):
                self.RenderTextRenderer(component)

        #Finally blit the render target onto the final display.
        self.game.display.blit(pygame.transform.scale(self._renderTarget,(self._screenSize[0],self._screenSize[1])),(0,0))
        pygame.display.update()

    def RenderSpriteRenderer(self,spriteRenderer : SpriteRenderer):
        if (spriteRenderer.sprite == None):
            return

        spriteSurface = GetSprite(spriteRenderer.sprite)
        # Validate if we found an actual sprite
        if (spriteSurface == None):
            return

        # Verify what is being drawn is on the screen
        if (False == self.IsOnScreenSprite(spriteSurface, spriteRenderer.parentEntity.position)):
            return

        finalPosition = self.FinalPositionOfSprite(spriteRenderer.parentEntity.position, spriteSurface, spriteRenderer.screenSpace)
        self._renderTarget.blit(spriteSurface, finalPosition)

        if (self.debug):  # If debug draw bounds of spriterenderers
            pygame.draw.rect(self._renderTarget, (255, 0, 0),
                             pygame.Rect(finalPosition[0] - 1, finalPosition[1], spriteSurface.get_width(),
                                         spriteSurface.get_height()), width=1)

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

                tailSprite : Sprite = GetSprite(tileMapRenderer.tileMap.tileSet[tileMapRenderer.tileMap.map[x][y]],True)
                spriteSurface = tailSprite.GetSprite()
                self._renderTarget.blit(spriteSurface, leftAnchoredScreenPosition)
                if (tailSprite._tint):
                    self._renderTarget.fill(color=tailSprite._tint, rect=(
                    leftAnchoredScreenPosition[0], leftAnchoredScreenPosition[1], spriteSurface.get_width(), spriteSurface.get_width()),
                                            special_flags=pygame.BLEND_ADD)

    def RenderParticleEmitter(self,emitter : ParticleEmitterComponent):
        if(emitter.sprite == None):
            return

        #See if a new particle should spawn, if so create it.
        for i in range(int((self.game.frameStartTime - emitter._lastParticleSpawnTime) * emitter.particlesPerSecond)):
            if (len(emitter._activeParticles) >= emitter.maxParticles):
                break
            emitter.NewParticle()
            emitter._lastParticleSpawnTime = self.game.frameStartTime

        #Now simulate and render all particles
        particle : Particle
        for particle in emitter._activeParticles[:]:
            #Simulate
            particle.lifeTime -= self.game.deltaTime
            if(particle.lifeTime <= 0):
                emitter._activeParticles.remove(particle)
                continue

            particle.velocity[0] += particle.gravity[0] * self.game.deltaTime
            particle.velocity[1] += particle.gravity[1] * self.game.deltaTime

            particle.position[0] += particle.velocity[0] * self.game.deltaTime
            particle.position[1] += particle.velocity[1] * self.game.deltaTime


            #Render
            if (self.IsOnScreenRect(pygame.Rect(particle.position[0], particle.position[1], particle.sprite.get_width(), particle.sprite.get_height()))):
                finalSprite = GetSprite(particle.sprite)
                self._renderTarget.blit(finalSprite,self.FinalPositionOfSprite(particle.position,finalSprite))

    def RenderTextRenderer(self,textRenderer : TextRenderer):
        if (textRenderer._render == None):
            return

        actualSprite = textRenderer._render.GetSprite()
        # Validate if we found an actual sprite
        if (actualSprite == None):
            return

        renderPosition = textRenderer.parentEntity.position
        if(textRenderer.screenSpace == True):
            #if in screen space convert to screen space
            renderPosition = self.WorldToScreenPosition(renderPosition)
        else:
            # If in world space, verify what is being drawn is on the screen
            if (False == self.IsOnScreenSprite(actualSprite, textRenderer.parentEntity.position)):
                return
            renderPosition = self.FinalPositionOfSprite(renderPosition, actualSprite, screenSpace=textRenderer.screenSpace)

        self._renderTarget.blit(actualSprite, [renderPosition[0] - textRenderer._render.get_width()//2,renderPosition[1] - textRenderer._render.get_height()//2])

    def WorldToScreenPosition(self,position):
        return [position[0] - self.cameraPosition[0] + self._scaledHalfSize[0], position[1] - self.cameraPosition[1] + self._scaledHalfSize[1]]

    def FinalPositionOfSprite(self,position,sprite, screenSpace=False):
        topLeftPosition = CenterToTopLeftPosition(position, sprite)
        if(not screenSpace):
            return self.WorldToScreenPosition(topLeftPosition)
        else:
            #for the user we center 0,0 on the screen but when drawing 0,0 is the top left. So we fix it here.
            return (topLeftPosition[0]+self._scaledHalfSize[0],topLeftPosition[1]+self._scaledHalfSize[1])

    def IsOnScreenSprite(self, sprite : pygame.Surface, position) -> bool:
        return self.IsOnScreenRect(pygame.Rect(position[0]-sprite.get_width()//2,position[1]-sprite.get_height()//2,sprite.get_width(),sprite.get_height()))

    def IsOnScreenRect(self,rect : pygame.Rect):
        screenBounds = pygame.Rect(self.cameraPosition[0] - self._scaledHalfSize[0],self.cameraPosition[1] - self._scaledHalfSize[1],self._scaledScreenSize[0],self._scaledScreenSize[1])
        return screenBounds.colliderect(rect)

    def DebugDrawWorldRect(self,color,rect):
        worldP = self.WorldToScreenPosition((rect.x,rect.y))
        pygame.draw.rect(self._renderTarget,(255,0,0),(worldP[0],worldP[1],rect.w,rect.h))