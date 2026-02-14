import random

import pygame.font

from engine.components.recttransformcomponent import RectTransformComponent
from engine.components.rendering.textrenderer import TextRenderer
from engine.constants import ALIGN_TOPLEFT
from engine.scenes.levelscene import LevelScene
from engine.systems.physics import PhysicsSystem
from engine.systems.ui import UISystem
from engine.tools.platform import IsPlatformWeb
from engine.tools.webutils import GetLocalStorage
from game import prefabs
from game.assets import worldTileset
from game.systems import playersystem
from game.systems.NPCSystem import NPCSystem


class TiledTestScene(LevelScene):
    loadWebCookies = True
    def __init__(self):
        super().__init__(random.choice(["game/art/tiled/testmap1.tmj"]),worldTileset, {"SKELETON" : prefabs.CreateSkeleton})
        self.name = "Tiled Test Scene"
        self.systems.append(playersystem.PlayerSystem())
        self.systems.append(NPCSystem())
        self.systems.append(PhysicsSystem())
        self.systems.append(UISystem())
        self.player = None
        
    def LevelStart(self):
        self.player = prefabs.CreatePlayer(self)
        self.player.position = self.GetRandomTiledObjectByName("SPAWN")["position"][:]
        if IsPlatformWeb() and TiledTestScene.loadWebCookies:
            TiledTestScene.loadWebCookies = False
            #self.player.position = [
            #    float(GetCookie("me_tts_pos_x", self.player.position[0])),
            #    float(GetCookie("me_tts_pos_y", self.player.position[1]))
            #]
            self.player.position = GetLocalStorage("me_tts_pos", self.player.position, "listfloat")

        self.worldTextTest = self.CreateEntity("World Text Test",[-150,0],[TextRenderer("World Test String :)", 12, "Arial")])
        self.worldTextTest.GetComponent(TextRenderer).screenSpace = False
        self.screenSpaceText = self.CreateEntity("Screen Text Test",[0,0],[TextRenderer("Screen Text Test", 12, "Arial"),
                                   RectTransformComponent(ALIGN_TOPLEFT,bounds=(0.5,0.1))])
        self.screenSpaceText.GetComponent(TextRenderer).screenSpace = True
        self.screenSpaceText.GetComponent(TextRenderer).SetAlign(ALIGN_TOPLEFT)

        def SpawnEnemyAbovePlayer(s,o):
            if(o.parentEntity.name == "Player"):
                newSkeleton = prefabs.CreateSkeleton(self)
                newSkeleton.position = [self.player.position[0], self.player.position[1] - 100]

        for i in range(5):
            p = prefabs.CreateParticleTestPrefab(self)
            p.position = self.GetRandomTiledObjectByName("SPAWN")["position"][:]

        if(self.GetTriggerByName("TEST TRIGGER") != None):
            self.GetTriggerByName("TEST TRIGGER").onTriggerStart.append(SpawnEnemyAbovePlayer)