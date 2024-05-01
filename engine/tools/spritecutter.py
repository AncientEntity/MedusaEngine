#THIS TOOL IS CURRENTLY INCOMPLETE AND DOESNT WORK
#Standalone utility that allows you to manually cut/create a sprite map as expected in spritesheet.py

import time

import pygame

class CutSprite:
    def __init__(self):
        self.rect = pygame.Rect(-1,-1,0,0)
        self.name = "unnamed"

class SpriteCutter:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600,600))
        self.cameraPosition = [0,0]
        self.zoom = 1
        self.running = False
        self.targetFilePath = ""
        self.spriteOriginal = None

        self.cutSprites : list[CutSprite] = [CutSprite()]
    def Run(self):
        self.running = True
        self.targetFilePath = "game\\art\\world_tileset.png" #input("Spritesheet file path: ")
        self.spriteOriginal = pygame.image.load(self.targetFilePath)

        lastFrameTime = time.time()
        lastMousePosition = pygame.mouse.get_pos()
        while self.running:
            #Handle delta time/mouse calculations
            deltaTime = time.time() - lastFrameTime
            lastFrameTime = time.time()
            mouseDelta = (pygame.mouse.get_pos()[0]-lastMousePosition[0],pygame.mouse.get_pos()[1]-lastMousePosition[1])
            lastMousePosition = pygame.mouse.get_pos()

            self.Update(deltaTime,mouseDelta)
            self.Render()



    def Update(self,deltaTime,mouseDelta):
        curSpriteCut = self.cutSprites[len(self.cutSprites) - 1]
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                exit(0)
            elif (event.type == pygame.MOUSEWHEEL): #Zooming in/out
                self.zoom += event.y * deltaTime * 60
            elif(event.type == pygame.KEYDOWN):
                if(event.key == pygame.K_BACKSPACE):
                    curSpriteCut.rect = pygame.Rect(-1,-1,0,0)

        if (pygame.mouse.get_pressed()[0]): #Moving the camera around
            self.cameraPosition[0] += mouseDelta[0]
            self.cameraPosition[1] += mouseDelta[1]
        elif(pygame.mouse.get_pressed()[2]):
            mousePosWorld = self.ScreenToWorldPosition(pygame.mouse.get_pos())
            mousePosWorld = [mousePosWorld[0],mousePosWorld[1]]
            if(curSpriteCut.rect.x == -1):
                curSpriteCut.rect.x = mousePosWorld[0]
                curSpriteCut.rect.y = mousePosWorld[1]
            else:
                curSpriteCut.rect.w = mousePosWorld[0]-curSpriteCut.rect.x
                curSpriteCut.rect.h = mousePosWorld[1]-curSpriteCut.rect.y

    def Render(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(pygame.transform.scale(self.spriteOriginal, (
        self.spriteOriginal.get_width() * self.zoom, self.spriteOriginal.get_height() * self.zoom)),
                         (self.cameraPosition))

        cutSprite : CutSprite
        for cutSprite in self.cutSprites:
            print(cutSprite.rect)
            screenPoint = self.WorldToScreenPoint([cutSprite.rect.x,cutSprite.rect.y])
            pygame.draw.rect(self.screen,(50,50,210),(screenPoint[0],screenPoint[1],cutSprite.rect.w,cutSprite.rect.h))

        pygame.display.update()

    def ScreenToWorldPosition(self,screenPos):
        return [round((screenPos[0]-self.cameraPosition[0])),round((screenPos[1]-self.cameraPosition[1]))]
    def WorldToScreenPoint(self,worldPos):
        return [round(worldPos[0]+self.cameraPosition[0]),round(worldPos[1]+self.cameraPosition[1])]


if __name__ == "__main__":
    input("Warning this currently is incomplete, input anything to continue.")
    cutter = SpriteCutter()
    cutter.Run()