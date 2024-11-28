from engine.game import Game
from game.scenes.dungeonscene import DungeonScene
from game.scenes.mainscene import MainScene


class TopdownGame(Game):
    def __init__(self):
        super().__init__()
        self.name = "Topdown Game Demo"
        self.startingScene = MainScene
        self.startingSplashEnabled = False
        self.windowSize : tuple(int) = (1280,800)