from engine.scenes.levelscene import LevelScene
from game import prefabs
from game.assets import worldTileset
from game.systems import playersystem
from game.systems.NPCSystem import NPCSystem


class TiledTestScene(LevelScene):
    def __init__(self):
        super().__init__("game/art/tiled/testmap1.tmj",worldTileset, {"SPAWN" : prefabs.CreatePlayer, "SKELETON" : prefabs.CreateSkeleton})
        self.systems.append(playersystem.PlayerSystem())
        self.systems.append(NPCSystem())