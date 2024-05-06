from engine.game import Game
from game.scenes import factoryscene


class TinyFactoryGame(Game):
    def __init__(self):
        super().__init__()
        self.name = "Tiny Factory in Medusa Engine"
        self.startingScene = factoryscene.TinyFactoryScene()
        self.startingSplashEnabled = False
        self.windowSize = (256*2,272*2)