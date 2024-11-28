from engine.ecs import Scene


class Game:
    def __init__(self):
        self.name = "Empty Game"
        self.startingScene : Scene = None
        self.startingSplashEnabled = True
        self.icon = None
        self.windowSize : tuple(int) = (800,600)
        self.startFullScreen = False

        self.webCanvasPixelated = True # Determine if the web canvas of a web build is pixelated or not.