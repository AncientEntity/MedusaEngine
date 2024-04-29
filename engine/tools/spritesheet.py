import pygame

from engine.logging import Log, LOG_WARNINGS, LOG_ALL


class SpriteSheet:
    #mapFile is optional but when provided spriteSize is ignored and it will read the map file to determine the rects of each sprite.
    #map file example at bottom of file
    def __init__(self, spriteFile, spriteSize,mapFile=None):
        self.spriteSize = spriteSize
        self.spriteFile = spriteFile
        self.mapFilePath = mapFile
        self.splitType = None

        self.full : pygame.Surface = pygame.image.load(spriteFile)
        print("[SpriteSheet] Loaded full: " + spriteFile)
        self.fullSize = self.full.get_size()
        self.sprites = {}

        if(mapFile == None):
            self.SplitFramesBasedOnSize()
            self.splitType = 'size'
        else:
            self.SplitFramesBasedOnMap()
            self.splitType = 'map'

    def SplitFramesBasedOnMap(self):
        if(self.mapFilePath == None):
            Log("Can't split frames based on map, no map provided.",LOG_WARNINGS)
            return
        mapFile = open(self.mapFilePath,"r")
        for line in mapFile.read().split("\n"):
            splitLine = line.split(" ")
            if(len(splitLine)< 5):
                Log("Invalid line in "+self.mapFilePath+", line: "+line,LOG_WARNINGS)
                continue
            subSprite = self.full.subsurface(pygame.Rect(int(splitLine[1]), int(splitLine[2]), int(splitLine[3]), int(splitLine[4])))
            self.sprites[splitLine[0]] = subSprite
            Log("Created "+splitLine[0] + " sprite frame",LOG_ALL)

        mapFile.close()

    def SplitFramesBasedOnSize(self):
        self.xCount = self.fullSize[0] // self.spriteSize
        self.yCount = self.fullSize[1] // self.spriteSize
        for x in range(self.xCount):
            for y in range(self.yCount):
                subSprite = self.full.subsurface(pygame.Rect(x * self.spriteSize, y * self.spriteSize, self.spriteSize, self.spriteSize))
                self.sprites[str(x) + ":" + str(y)] = subSprite
                print("[SpriteSheet] Loaded sprite from spritesheet(" + self.spriteFile + "): " + str(x) + ", " + str(y))
    def __getitem__(self,item : tuple or str) -> pygame.Surface:
        if(type(item) == tuple):
            return self.sprites[str(item[0])+":"+str(item[1])]
        else:
            return self.sprites[item]

#Map file example (each line has name of frame, and x,y,w,h of rect:
#orc_shaman_idle_anim_f0 368 201 16 23
#orc_shaman_idle_anim_f1 384 201 16 23
#orc_shaman_idle_anim_f2 400 201 16 23
#orc_shaman_idle_anim_f3 416 201 16 23
#orc_shaman_run_anim_f0 432 201 16 23
#orc_shaman_run_anim_f1 448 201 16 23
#orc_shaman_run_anim_f2 464 201 16 23
#orc_shaman_run_anim_f3 480 201 16 23
#swampy_anim_f0 432 112 16 16
#swampy_anim_f1 448 112 16 16
#swampy_anim_f2 464 112 16 16
#swampy_anim_f3 480 112 16 16
#muddy_anim_f0 368 112 16 16
#muddy_anim_f1 384 112 16 16
#muddy_anim_f2 400 112 16 16
#muddy_anim_f3 416 112 16 16
#necromancer_anim_f0 368 225 16 23
#necromancer_anim_f1 384 225 16 23
#necromancer_anim_f2 400 225 16 23
#necromancer_anim_f3 416 225 16 23
#masked_orc_idle_anim_f0 368 153 16 23
#masked_orc_idle_anim_f1 384 153 16 23
#masked_orc_idle_anim_f2 400 153 16 23