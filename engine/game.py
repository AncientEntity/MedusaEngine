from pygame import K_w, K_s, K_a, K_d

from engine.constants import SPLASH_BUILDONLY
from engine.datatypes.inputaction import InputAction
from engine.ecs import Scene
from engine.networking.transport.networktcptransport import NetworkTCPTransport


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

        self.inputActions = {
            'up' : InputAction("up", K_w, True),
            'down' : InputAction("down", K_s, True),
            'left' : InputAction("left", K_a, True),
            'right' : InputAction("right", K_d, True),
        }

        # Multiplayer
        self.transportName = "tcp"
        self.transportClass = NetworkTCPTransport