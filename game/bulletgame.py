from engine.game import Game
from game.scenes.levelscene import LevelScene


class BulletGame(Game):
    def __init__(self):
        super().__init__()
        self.name = "Bullet Game"
        self.startingScene = LevelScene
        self.startingSplashEnabled = False