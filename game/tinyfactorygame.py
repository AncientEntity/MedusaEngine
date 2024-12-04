from engine.game import Game
from game.scenes import factoryscene


class TinyFactoryGame(Game):
    def __init__(self):
        super().__init__()
        self.name = "Tiny Factory in Medusa Engine"
        self.startingScene = factoryscene.TinyFactoryScene #Past as class not object.
        self.windowSize = (256*2,272*2)