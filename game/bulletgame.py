from engine.game import Game
from game.scenes.sidescrollingscene import SideScrollingScene
from game.scenes.tiledtestscene import TiledTestScene


class BulletGame(Game):
    def __init__(self):
        super().__init__()
        self.name = "Bullet Game"
        self.startingScene = SideScrollingScene()
        self.startingSplashEnabled = False