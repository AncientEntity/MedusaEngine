import pygame
class SpriteSheet:
    def __init__(self,file,spriteSize):
        self.full : pygame.Surface = pygame.image.load(file)
        print("[SpriteSheet] Loaded full: "+file)
        self.fullSize = self.full.get_size()
        self.sprites = {}
        xCount = self.fullSize[0] // spriteSize
        yCount = self.fullSize[1] // spriteSize
        for x in range(xCount):
            for y in range(yCount):
                subSprite = self.full.subsurface(pygame.Rect(x*spriteSize,y*spriteSize,spriteSize,spriteSize))
                self.sprites[str(x)+":"+str(y)] = subSprite
                print("[SpriteSheet] Loaded sprite from spritesheet("+file+"): "+str(x)+", "+str(y))
    def __getitem__(self,item : tuple) -> pygame.Surface:
        return self.sprites[str(item[0])+":"+str(item[1])]