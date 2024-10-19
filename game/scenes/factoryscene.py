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
        self.GetSystemByClass(renderer.RenderingSystem).renderScale = 2
    def LevelStart(self):
        self.music = self.CreateEntity("Music",[0,0],[AudioPlayer(RandomAudioClip(["game/sound/A Loop.ogg","game/sound/B Loop.ogg"]),True,0.4)])
        self.music.GetComponent(AudioPlayer).loops = True

        # Replace static conveyor sprites with animated ones

        self.tileMapLayersByName["Objects"].tileMap.SetSpriteAtIndex(AnimatedSprite([self.worldTileset.sprites[4], self.worldTileset.sprites[28],
                                                                                     self.worldTileset.sprites[36],self.worldTileset.sprites[44]], 16), 4)
        self.tileMapLayersByName["Objects"].tileMap.SetSpriteAtIndex(AnimatedSprite([self.worldTileset.sprites[5], self.worldTileset.sprites[29],
                                                                                     self.worldTileset.sprites[37],self.worldTileset.sprites[45]], 16), 5)
        self.tileMapLayersByName["Objects"].tileMap.SetSpriteAtIndex(AnimatedSprite([self.worldTileset.sprites[6], self.worldTileset.sprites[30],
                                                                                     self.worldTileset.sprites[38],self.worldTileset.sprites[46]], 16), 6)
        self.tileMapLayersByName["Objects"].tileMap.SetSpriteAtIndex(AnimatedSprite([self.worldTileset.sprites[7], self.worldTileset.sprites[31],
                                                                                     self.worldTileset.sprites[39],self.worldTileset.sprites[47]], 16), 7)