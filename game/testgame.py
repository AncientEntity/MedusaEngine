from engine.game import Game
from game.scenes.testing.TestScene import TestScene


class TestGame(Game):
    def __init__(self):
        super().__init__()
        self.startingScene = TestScene