import pygame, time


#Get Sprite
# getTailSprite determines if it will stop at the pygame.Surface, if True it will stop at the last 'Sprite' object before a surface.
def GetSprite(sprite, getTailSprite=False):
    if(isinstance(sprite,pygame.Surface)):
        return sprite
    else:
        nextSprite = sprite.GetSprite()
        if(getTailSprite == True and isinstance(nextSprite,pygame.Surface)):
            return sprite
        return nextSprite

class Sprite: #TODO sprite draw order implementation to control draw order.
    def __init__(self,filePathOrSurface : str or pygame.Surface):
        if(isinstance(filePathOrSurface,str)):
            if(filePathOrSurface != ""):
                self._unmodifiedSprite = pygame.image.load(filePathOrSurface)
            else:
                self._unmodifiedSprite = None
        elif(isinstance(filePathOrSurface,pygame.Surface)):
            self._unmodifiedSprite = filePathOrSurface
        self._flipX = False
        self.ignoreCollision = False
        self.tint = None
        self.sprite = None # Set in self.RefreshSprite ran below.
        self.RefreshSprite()

    #Regenerates self.sprite from self._unmodifiedSprite based on modifiers such as self.tint
    def RefreshSprite(self):
        spriteCopy = self._unmodifiedSprite.copy()

        #Handle tint
        if(self.tint != None):
            spriteCopy.fill(self.tint)

        #Handle rotation todo unimplemented

        self.sprite = spriteCopy

        #Handle FlipX
        self.FlipX(self._flipX)

    def GetSprite(self):
        return self.sprite
    def FlipX(self,flipped):
        if(flipped == self._flipX):
            return

        self._flipX = flipped
        if(isinstance(self.sprite,pygame.Surface)):
            self.sprite = pygame.transform.flip(self._unmodifiedSprite,True,False)
        else:
            self.sprite.FlipX(flipped)
    def SetTint(self,tint):
        self.tint = tint
        self.RefreshSprite()
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