from engine.components.audioplayer import AudioPlayer
from engine.datatypes.audioclip import RandomAudioClip
from engine.datatypes.sprites import AnimatedSprite
from engine.scenes.levelscene import LevelScene
from engine.systems import renderer
from engine.systems.audio import AudioSystem
from engine.systems.physics import PhysicsSystem
from engine.systems.ui import UISystem
from game.constants import worldSpriteSheet
from game.systems.generatorsystem import GeneratorSystem
from game.systems.itemsystem import ItemSystem
from game.systems.gamesystem import GameSystem
from game.systems.notificationsystem import NotificationSystem

class TinyFactoryScene(LevelScene):
    def __init__(self):
        super().__init__("game/tiled/factorymap.tmj", worldSpriteSheet, None)
        self.systems.append(PhysicsSystem())
        self.systems.append(GameSystem())
        self.systems.append(ItemSystem())
        self.systems.append(GeneratorSystem())
        self.systems.append(NotificationSystem())
        self.systems.append(UISystem())
        self.systems.append(AudioSystem())
        self.GetSystemByClass(renderer.RenderingSystem).overrideRenderScale = 2
    def LevelStart(self):
        self.music = self.CreateEntity("Music",[0,0],[AudioPlayer(RandomAudioClip(["game/sound/A Loop.ogg","game/sound/B Loop.ogg"]),True,0.4)])
        self.music.GetComponent(AudioPlayer).loops = True

        # Replace static conveyor sprites with animated ones

        self.tileMapLayersByName["Objects"].tileMap.SetSpriteAtIndex(AnimatedSprite([self.worldTileset.spriteList[4], self.worldTileset.spriteList[28],
                                                                                     self.worldTileset.spriteList[36],self.worldTileset.spriteList[44]], 16), 4)
        self.tileMapLayersByName["Objects"].tileMap.SetSpriteAtIndex(AnimatedSprite([self.worldTileset.spriteList[5], self.worldTileset.spriteList[29],
                                                                                     self.worldTileset.spriteList[37],self.worldTileset.spriteList[45]], 16), 5)
        self.tileMapLayersByName["Objects"].tileMap.SetSpriteAtIndex(AnimatedSprite([self.worldTileset.spriteList[6], self.worldTileset.spriteList[30],
                                                                                     self.worldTileset.spriteList[38],self.worldTileset.spriteList[46]], 16), 6)
        self.tileMapLayersByName["Objects"].tileMap.SetSpriteAtIndex(AnimatedSprite([self.worldTileset.spriteList[7], self.worldTileset.spriteList[31],
                                                                                     self.worldTileset.spriteList[39],self.worldTileset.spriteList[47]], 16), 7)

        import sys
        print("PLAT:",sys.platform)