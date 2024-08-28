import pygame

from engine.logging import Log, LOG_INFO


class Console:
    cVars = {}
    def __init__(self):
        self.initialized = False
        self.enabled = False

        self.font : pygame.Font = None

        self.textHistory = []
        self.inputText = None


    def Init(self):
        self.font = pygame.font.Font("engine/art/console_font.ttf")


        Log("Console Initialized", LOG_INFO)

    def Tick(self, display : pygame.Surface):
        pass