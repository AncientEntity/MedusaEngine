from engine.ecs import Scene


class Game:
    def __init__(self):
        self.name = "Empty Game"
        self.startingScene : Scene = None
        self.startingSplashEnabled = True
        self.icon = None