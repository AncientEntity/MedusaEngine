from engine.constants import SPLASH_BUILDONLY
from engine.ecs import Scene


class Game:
    def __init__(self):
        self.name = "Empty Game"
        self.startingScene : Scene = None
        self.startingSplashMode = SPLASH_BUILDONLY
        self.icon = None

        self.windowSize : tuple(int) = (800,600)
        self.startFullScreen = False
        self.resizableWindow = False # Will not be enabled on web platform

        self.webCanvasPixelated = True # Determine if the web canvas of a web build is pixelated or not.