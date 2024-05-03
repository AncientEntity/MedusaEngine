from engine.scenes.levelscene import LevelScene
from game import prefabs
from game.assets import worldTileset
from game.systems import playersystem
from game.systems.NPCSystem import NPCSystem


class TiledTestScene(LevelScene):
    def __init__(self):
        super().__init__("game/art/tiled/testmap1.tmj",worldTileset, {"SKELETON" : prefabs.CreateSkeleton})
        self.systems.append(playersystem.PlayerSystem())
        self.systems.append(NPCSystem())
        self.player = None
    def LevelStart(self):
        self.player = prefabs.CreatePlayer(self)
        self.player.position = self.GetRandomTiledObjectByName("SPAWN")["position"]

        def SpawnEnemyAbovePlayer(s,o):
            if(o.parentEntity.name == "Player"):
                newSkeleton = prefabs.CreateSkeleton(self)
                newSkeleton.position = [self.player.position[0], self.player.position[1] - 100]

        self.GetTriggerByName("TEST TRIGGER").onTriggerStart.append(SpawnEnemyAbovePlayer)