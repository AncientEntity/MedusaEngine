from engine.game import Game
from game.scenes.mainscene import MainScene


class JamGame(Game):
    def __init__(self):
        super().__init__()
        self.name = "UVGD Jam Game"
        self.startingScene = MainScene
        self.startingSplashEnabled = False