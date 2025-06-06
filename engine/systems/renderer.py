import pygame.display

import engine.tools.platform
from engine.components.rendering.particlecomponent import ParticleEmitterComponent, Particle
from engine.components.rendering.renderercomponent import RendererComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.components.rendering.textrenderer import TextRenderer
from engine.components.rendering.tilemaprenderer import TilemapRenderer
from engine.datatypes.sprites import GetSprite, Sprite
from engine.ecs import EntitySystem, Scene
from engine.input import Input
from engine.logging import Log, LOG_ALL, LOG_INFO


def CenterToTopLeftPosition(centerPosition, surface : pygame.Surface):
    return [centerPosition[0]-surface.get_width()/2,centerPosition[1]-surface.get_height()/2]

class RenderingSystem(EntitySystem):
    instance = None
    def __init__(self):
        super().__init__([SpriteRenderer,TilemapRenderer,ParticleEmitterComponent,TextRenderer])
        self.removeOnHeadless = True

        self.cameraPosition = [0,0]
        self.worldPixelsToScreenPixels = (3.0 / 800.0)
        self.overrideRenderScale = None
        self.backgroundColor = (255,255,255)
        self.debug = False

        # Screen Data
        self._renderScale = 3
        self._renderTarget = None
        self._screenSize = None
        self._scaledScreenSize = None
        self._scaledHalfSize = None

        self.onScreenUpdated = [] # Whenever a screen setting is changed (resolution/fullscreen)

        self._sortedDrawOrder : list = [] #Sorted list of related components (ie SpriteRenderer). Sorted by sort order.

        self.rawMousePosition = (0, 0)
        self.screenMousePosition = (0, 0)
        self.worldMousePosition = (0,0)

    def __del__(self):
        if self in Input.onWindowResized:
            Input.onWindowResized.pop(self)

    def OnEnable(self, currentScene : Scene):
        RenderingSystem.instance = self
        if not engine.tools.platform.headless:
            Input.onWindowResized[self] = self.InitializeScreenData
            self.InitializeScreenData()

    def OnNewComponent(self,component : RendererComponent):
        self.InsertIntoSortedRenderOrder(component)
        Log("Added "+component.parentEntity.name + " to rendering order."+str(component.drawOrder),LOG_ALL)

    def OnDeleteComponent(self, component : RendererComponent):
        indexOfComponent = self._sortedDrawOrder.index(component)
        if(indexOfComponent != -1):
            self._sortedDrawOrder.pop(indexOfComponent)
            Log("Removed "+component.parentEntity.name+" from rendering order.",LOG_ALL)

    def SetResolution(self, resolution, isFullscreen : bool):
        # If size is (0,0) then it uses the current screen resolution.
        pygame.display.set_mode((0,0) if isFullscreen else resolution, flags=pygame.FULLSCREEN if isFullscreen else 0)
        self.InitializeScreenData()
        Log(f"SetResolution({resolution},{isFullscreen})", LOG_INFO)

    def InitializeScreenData(self):
        self.CalculateRenderScale()
        self._screenSize = [self.game.display.get_width(),self.game.display.get_height()]
        self._scaledScreenSize = [self.game.display.get_width() / self._renderScale, self.game.display.get_height() / self._renderScale]
        self._scaledHalfSize = [self._scaledScreenSize[0]/2,self._scaledScreenSize[1]/2]
        self._renderTarget = pygame.Surface(self._scaledScreenSize)
        for func in self.onScreenUpdated:
            func()
        Log(f"InitializeScreenData Completed RenderScale={self._renderScale}", LOG_INFO)

    def CalculateRenderScale(self):
        if self.overrideRenderScale:
            self._renderScale = self.overrideRenderScale
            return

        if self.game.display.get_width() > self.game.display.get_height():
            self._renderScale = self.game.display.get_width() * self.worldPixelsToScreenPixels
        else:
            self._renderScale = self.game.display.get_height() * self.worldPixelsToScreenPixels

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
        if engine.tools.platform.headless:
            return

        self._renderTarget.fill(self.backgroundColor)

        self.rawMousePosition = pygame.mouse.get_pos()
        self.screenMousePosition = ((self.rawMousePosition[0] - self._screenSize[0] / 2) / self._renderScale, (self.rawMousePosition[1] - self._screenSize[1] / 2) / self._renderScale)
        self.worldMousePosition = (self.screenMousePosition[0]+self.cameraPosition[0],
                                   self.screenMousePosition[1]+self.cameraPosition[1])

        #Loop through sorted render order and render everything out.
        component : RendererComponent
        for component in self._sortedDrawOrder:
            if not component.enabled:
                continue
            if(isinstance(component,SpriteRenderer)):
                self.RenderSpriteRenderer(component)
            elif(isinstance(component,TilemapRenderer)):
                worldPositionTopLeft = (self.cameraPosition[0]-self._scaledHalfSize[0],self.cameraPosition[1]-self._scaledHalfSize[1])
                worldDrawBounds = pygame.FRect(worldPositionTopLeft[0],worldPositionTopLeft[1],self._scaledScreenSize[0],self._scaledScreenSize[1])
                self.RenderTileMapRenderer(component, worldDrawBounds)
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
        if (False == self.IsOnScreenSprite(spriteSurface, spriteRenderer.parentEntity.position, spriteRenderer.screenSpace)):
            return

        finalPosition = self.FinalPositionOfSprite(spriteRenderer.parentEntity.position, spriteSurface, spriteRenderer.screenSpace)
        self._renderTarget.blit(spriteSurface, finalPosition)

        if (self.debug):  # If debug draw bounds of spriterenderers
            pygame.draw.rect(self._renderTarget, (255, 0, 0),
                             pygame.Rect(finalPosition[0] - 1, finalPosition[1], spriteSurface.get_width(),
                                         spriteSurface.get_height()), width=1)

    def RenderTileMapRenderer(self,tileMapRenderer : TilemapRenderer, worldDrawBounds):
        if (tileMapRenderer.tileMap == None or tileMapRenderer.tileMap.tileSet == None):
            return

        topLeftTilePos = tileMapRenderer.WorldPositionToTileIndex(worldDrawBounds.topleft)
        bottomRightTilePos = tileMapRenderer.WorldPositionToTileIndex(worldDrawBounds.bottomright)
        tileDrawBounds = tileMapRenderer.GetOverlappingTilesInWorldSpace(topLeftTilePos, bottomRightTilePos, True)

        for (tileID, (x,y)) in tileDrawBounds:

            leftAnchoredScreenPosition = self.WorldToScreenPosition((x,y))

            tailSprite : Sprite = GetSprite(tileMapRenderer.tileMap.tileSet[tileID],True)
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

    def RenderTextRenderer(self, textRenderer: TextRenderer):
        if (textRenderer._render == None):
            return

        actualSprite = textRenderer._render.GetSprite()
        # Validate if we found an actual sprite
        if (actualSprite == None):
            return

        renderPosition = (textRenderer.parentEntity.position[0] - textRenderer._alignOffset[0],
                          textRenderer.parentEntity.position[1] - textRenderer._alignOffset[1])

        if not textRenderer.screenSpace:
            renderPosition = self.WorldToScreenPosition(renderPosition)
        else:
            #for the user we center 0,0 on the screen but when drawing 0,0 is the top left. So we fix it here.
            renderPosition = (renderPosition[0] + self._scaledHalfSize[0], renderPosition[1] + self._scaledHalfSize[1])

        self._renderTarget.blit(actualSprite, (renderPosition[0], renderPosition[1]))

        # Debug circle at parent entity position todo remove this once certain feature works as should.
        #pygame.draw.circle(self._renderTarget, (0, 0, 255),
        #                   self.WorldToScreenPosition(textRenderer.parentEntity.position), 2)

    def WorldToScreenPosition(self,position):
        return [round(position[0] - self.cameraPosition[0] + self._scaledHalfSize[0]), round(position[1] - self.cameraPosition[1] + self._scaledHalfSize[1])]
    def ScreenToWorldPosition(self, position):
        return [position[0] + self.cameraPosition[0] - self._scaledHalfSize[0], position[1] + self.cameraPosition[1] - self._scaledHalfSize[1]]

    def FinalPositionOfSprite(self,position,sprite, screenSpace=False):
        topLeftPosition = CenterToTopLeftPosition(position, sprite)
        if(not screenSpace):
            return self.WorldToScreenPosition(topLeftPosition)
        else:
            #for the user we center 0,0 on the screen but when drawing 0,0 is the top left. So we fix it here.
            return (topLeftPosition[0]+self._scaledHalfSize[0],topLeftPosition[1]+self._scaledHalfSize[1])

    def IsOnScreenSprite(self, sprite : pygame.Surface, position, screenSpace=False) -> bool:
        if not screenSpace:
            return self.IsOnScreenRect(pygame.Rect(position[0]-sprite.get_width()//2,position[1]-sprite.get_height()//2,sprite.get_width(),sprite.get_height()))
        else:
            return self.IsOnScreenSpaceRect(pygame.Rect(position[0]-sprite.get_width()//2,position[1]-sprite.get_height()//2,sprite.get_width(),sprite.get_height()))

    def IsOnScreenRect(self,rect : pygame.Rect):
        screenBounds = pygame.Rect(self.cameraPosition[0] - self._scaledHalfSize[0],self.cameraPosition[1] - self._scaledHalfSize[1],self._scaledScreenSize[0],self._scaledScreenSize[1])
        return screenBounds.colliderect(rect)
    def IsOnScreenPoint(self, point):
        screenBounds = pygame.Rect(self.cameraPosition[0] - self._scaledHalfSize[0],
                                   self.cameraPosition[1] - self._scaledHalfSize[1], self._scaledScreenSize[0],
                                   self._scaledScreenSize[1])
        return screenBounds.collidepoint(point[0],point[1])

    def IsOnScreenSpaceRect(self, rect : pygame.Rect):
        screenBounds = pygame.Rect(-self._scaledHalfSize[0],-self._scaledHalfSize[1],self._scaledScreenSize[0],self._scaledScreenSize[1])
        return screenBounds.colliderect(rect)

    def DebugDrawWorldRect(self,color,rect):
        worldP = self.WorldToScreenPosition((rect.x,rect.y))
        pygame.draw.rect(self._renderTarget,color,(worldP[0],worldP[1],rect.w,rect.h),1)