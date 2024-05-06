from engine.game import Game

class TinyFactoryGame(Game):
    def __init__(self):
        super().__init__()
        self.name = "Bullet Game"
        self.startingScene = None
        self.startingSplashEnabled = False