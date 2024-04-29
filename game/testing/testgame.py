from engine.game import Game
from game.testing.scenes.testing.TestScene import TestScene


class TestGame(Game):
    def __init__(self):
        super().__init__()
        self.name = "Test Game"
        self.startingScene = TestScene
        self.startingSplashEnabled = False