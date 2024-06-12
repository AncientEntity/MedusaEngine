from engine.datatypes.spritesheet import SpriteSheet
from engine.scenes.levelscene import LevelScene

class ${NAME}(LevelScene):
    def __init__(self):
        super().__init__("game/tiled/changeme.tmj", SpriteSheet("game/art/changeme.png",16), None)
        
        #Append systems here like this: self.systems.append()
        #By default a LevelScene just has a rendering system.