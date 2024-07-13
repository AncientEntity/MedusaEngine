from engine.game import Game
from game.scenes.pathfindingscene import PathfindingScene


class PathfindingGame(Game):
    def __init__(self):
        super().__init__()
        self.name = "Bullet Game"
        self.startingScene = PathfindingScene
        self.startingSplashEnabled = False
        self.windowSize = (800,800)