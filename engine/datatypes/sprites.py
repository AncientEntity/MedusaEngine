import pygame, time


def GetSprite(sprite):
    if(isinstance(sprite,pygame.Surface)):
        return sprite
    else:
        return sprite.GetSprite()

class Sprite: #TODO sprite draw order implementation to control draw order.
    def __init__(self,filePathOrSurface : str or pygame.Surface):
        if(isinstance(filePathOrSurface,str)):
            if(filePathOrSurface != ""):
                self.sprite = pygame.image.load(filePathOrSurface)
            else:
                self.sprite = None
        elif(isinstance(filePathOrSurface,pygame.Surface)):
            self.sprite = filePathOrSurface
        self._flipX = False
        self.ignoreCollision = False
    def GetSprite(self):
        return self.sprite
    def FlipX(self,flipped):
        if(flipped == self._flipX):
            return

        self._flipX = flipped
        if(isinstance(self.sprite,pygame.Surface)):
            self.sprite = pygame.transform.flip(self.sprite,True,False)
        else:
            self.sprite.FlipX(flipped)
    def get_width(self):
        return self.sprite.get_width()
    def get_height(self):
        return self.sprite.get_height()

class AnimatedSprite(Sprite):
    def __init__(self,sprites,fps):
        super().__init__("")
        self.timer = 0
        self.sprites = sprites
        self.fps = fps
        self.lastTime = time.time()
    def GetSprite(self):
        self.timer += (time.time() - self.lastTime)
        self.lastTime = time.time()
        targetSprite = self.sprites[int((self.timer * self.fps) % len(self.sprites))]
        if isinstance(targetSprite, pygame.Surface):
            return targetSprite
        elif(isinstance(targetSprite,Sprite)):
            return targetSprite.GetSprite()
    def FlipX(self,flipped):
        if(flipped == self._flipX):
            return

        self._flipX = flipped
        for i in range(len(self.sprites)):
            if(isinstance(self.sprites[i],pygame.Surface)):
                self.sprites[i] = pygame.transform.flip(self.sprites[i],True,False)
            else:
                self.sprites[i].FlipX(flipped)
    def get_width(self):
        return self.GetSprite().get_width()
    def get_height(self):
        return self.GetSprite().get_height()