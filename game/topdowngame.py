from engine.game import Game
from game.scenes.mainscene import MainScene


class TopdownGame(Game):
    def __init__(self):
        super().__init__()
        self.name = "Topdown Game Demo"
        self.startingScene = MainScene
        self.startingSplashEnabled = False