import pygame

from engine.scenes.levelscene import LevelScene
from game import prefabs
from game.assets import worldTileset
from game.systems import playersystem
from game.systems.NPCSystem import NPCSystem
from game.systems.playersystem import PlayerComponent


class TiledTestScene(LevelScene):
    def __init__(self):
        super().__init__("game/art/tiled/testmap1.tmj",worldTileset, {"SKELETON" : prefabs.CreateSkeleton})
        self.systems.append(playersystem.PlayerSystem())
        self.systems.append(NPCSystem())
    def LevelStart(self):
        prefabs.CreatePlayer(self).position = self.GetRandomTiledObjectByName("SPAWN")["position"]
        #p2 = prefabs.CreatePlayer(self)
        #p2.position = self.GetRandomTiledObjectByName("SPAWN")["position"]
        #p2.GetComponent(PlayerComponent).controls = {'up' : pygame.K_UP, 'down' : pygame.K_DOWN, 'left' : pygame.K_LEFT, 'right' : pygame.K_RIGHT}