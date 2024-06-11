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
        self.sprite = None  # Set in self.RefreshSprite ran at bottom of __init__.

        self._flipX = False
        self.ignoreCollision = False
        self.tint = None
        self._rotation = None

        self.RefreshSprite()

    #Regenerates self.sprite from self._unmodifiedSprite based on modifiers such as self.tint
    def RefreshSprite(self):
        if(self._unmodifiedSprite == None):
            return

        self.sprite = self._unmodifiedSprite.copy()

        #todo render offset (where you can have an offset and it repeats). ex: if you have a conveyor belt sprite you can 'repeat' it with an offset.

        #Handle tint
        if(self.tint != None):
            self.sprite.fill(self.tint,special_flags=pygame.BLEND_ADD)

        #Handle FlipX
        if(self._flipX):
            self.sprite = pygame.transform.flip(self.sprite, True, False)

        #Handle rotation
        if(self._rotation):
            self.sprite = pygame.transform.rotate(self.sprite,self._rotation)

    def GetSprite(self):
        return self.sprite
    def SetFlipX(self, flipped):
        if(self._flipX == flipped):
            return

        self._flipX = flipped
        self.RefreshSprite()

    def SetTint(self,tint):
        if(self.tint == tint):
            return

        self.tint = tint
        self.RefreshSprite()
    def SetRotation(self,rotation):
        if(self._rotation == rotation):
            return

        self._rotation = rotation
        self.RefreshSprite()

    def get_width(self):
        return self.sprite.get_width()
    def get_height(self):
        return self.sprite.get_height()

class AnimatedSprite(Sprite):
    def __init__(self,sprites,fps):
        super().__init__("")
        self.timer = 0
        self.fps = fps
        self.lastTime = time.time()

        self._sprites = []
        self.AddSprites(sprites)
    def AddSprite(self,sprite):
        if(isinstance(sprite,pygame.Surface)):
            self._sprites.append(Sprite(sprite))
        else:
            self._sprites.append(sprite)
    def AddSprites(self,sprites):
        for sprite in sprites:
            self.AddSprite(sprite)
    def ReplaceSprite(self,sprite,index):
        if(isinstance(sprite,pygame.Surface)):
            self._sprites[index] = Sprite(sprite)
        else:
            self._sprites[index] = sprite
    def InsertSprite(self,sprite,index):
        if(isinstance(sprite,pygame.Surface)):
            self._sprites.insert(index, Sprite(sprite))
        else:
            self._sprites.insert(index,sprite)

    def GetSprite(self):
        self.timer += (time.time() - self.lastTime)
        self.lastTime = time.time()
        targetSprite = self._sprites[int((self.timer * self.fps) % len(self._sprites))]
        if isinstance(targetSprite, pygame.Surface):
            return targetSprite
        elif(isinstance(targetSprite,Sprite)):
            return targetSprite.GetSprite()
    def SetFlipX(self, flipped):
        if(self._flipX == flipped):
            return

        self._flipX = flipped
        for i in range(len(self._sprites)):
            if(isinstance(self._sprites[i], pygame.Surface)):
                self._sprites[i] = pygame.transform.flip(self._sprites[i], True, False)
            else:
                self._sprites[i].SetFlipX(flipped)
    def SetTint(self,tint):
        for sprite in self._sprites:
            sprite.SetTint(tint)
    def SetRotation(self,rotation):
        for sprite in self._sprites:
            sprite.SetRotation(rotation)
    def get_width(self):
        return self.GetSprite().get_width()
    def get_height(self):
        return self.GetSprite().get_height()