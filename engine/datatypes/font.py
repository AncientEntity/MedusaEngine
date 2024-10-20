import os.path

import pygame.font


class Font:
    def __init__(self, fontSysNameOrFile : str):
        self._fontSource = fontSysNameOrFile
        self._isSysFont = not os.path.isfile(fontSysNameOrFile)

    def GetPygameFont(self, fontSize, bold=False, italic=False):
        if self._isSysFont:
            return pygame.font.SysFont(self._fontSource, fontSize, bold, italic)
        else:
            return pygame.font.Font(self._fontSource, fontSize)
