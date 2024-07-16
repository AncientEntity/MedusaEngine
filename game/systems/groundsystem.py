from engine.components.rendering.tilemaprenderer import TilemapRenderer
from engine.ecs import EntitySystem, Scene
import random

class GroundSystem(EntitySystem):
    def __init__(self):
        super().__init__([TilemapRenderer]) #Put target components here

        self.groundSprites = [129, 162, 131, 130, 161, 294]
        self.breakChances =  [1,   2,   4,   12,   16,   16]

    def Update(self,currentScene : Scene):
        tilemap : TilemapRenderer
        for tilemap in currentScene.components[TilemapRenderer]:
            if(tilemap.parentEntity.name == "WORLD-Ground"):
                for x in range(len(tilemap.tileMap.map)):
                    for y in range(len(tilemap.tileMap.map[0])):
                        tileID = tilemap.tileMap.GetTileID(x,y)
                        if(tileID == -1):
                            continue
                        index = self.groundSprites.index(tileID)
                        if(index == -1):
                            continue
                        if random.randint(0,20000) <= self.breakChances[index]:
                            if(index == len(self.breakChances)-1):
                                tilemap.tileMap.SetTile(-1,x,y)
                            else:
                                tilemap.tileMap.SetTile(self.groundSprites[index+1],x,y)
    def OnEnable(self, currentScene : Scene):
        pass
    def OnNewComponent(self,component : TilemapRenderer): #Called when a new component is created into the scene. (Used to initialize that component)
        pass
    def OnDeleteComponent(self, component : TilemapRenderer): #Called when an existing component is destroyed (Use for deinitializing it from the systems involved)
        pass