from engine.components.audioplayer import AudioPlayer
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
import random

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
        self.music = self.CreateEntity("Music",[0,0],[AudioPlayer(random.choice(["game/sound/A Loop.ogg","game/sound/B Loop.ogg"]),True,0.4)])
        self.music.GetComponent(AudioPlayer).loops = True