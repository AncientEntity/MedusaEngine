from engine.scenes.levelscene import LevelScene


class TinyFactoryScene(LevelScene):
    def __init__(self):
        super().__init__("tiledFilePath", "worldTileset", "objectMap")