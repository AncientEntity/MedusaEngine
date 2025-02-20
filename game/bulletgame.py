from engine.constants import SPLASH_ALWAYS
from engine.game import Game
from game.scenes.sidescrollingscene import SideScrollingScene
from game.scenes.tiledtestscene import TiledTestScene


class BulletGame(Game):
    def __init__(self):
        super().__init__()
        self.name = "Bullet Game"
        self.startingScene = TiledTestScene
        self.startingSplashMode = SPLASH_ALWAYS