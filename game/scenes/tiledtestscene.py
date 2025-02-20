import random

import pygame.font

from engine.components.recttransformcomponent import RectTransformComponent
from engine.components.rendering.textrenderer import TextRenderer
from engine.constants import ALIGN_TOPLEFT, NET_HOST
from engine.datatypes.assetmanager import assets
from engine.logging import Log
from engine.networking.networkstate import NetworkState
from engine.scenes.levelscene import LevelScene
from engine.systems.physics import PhysicsSystem
from engine.systems.ui import UISystem
from engine.tools.platform import IsPlatformWeb
from game.assets import worldTileset
from game.systems import playersystem
from game.systems.NPCSystem import NPCSystem


class TiledTestScene(LevelScene):
    def __init__(self):
        super().__init__(random.choice(["game/art/tiled/testmap1.tmj"]),worldTileset, {"SKELETON" : assets.FactoryInstantiate("skeleton")})
        self.name = "Tiled Test Scene"
        self.systems.append(playersystem.PlayerSystem())
        self.systems.append(NPCSystem())
        self.systems.append(PhysicsSystem())
        self.systems.append(UISystem())
        self.player = None

        NetworkState.onDisconnect["ondisconnect"] = self.OnDisconnect

        
    def LevelStart(self):
        if IsPlatformWeb():
            self.player = assets.Instantiate("player", self)
            self.player.position = self.GetRandomTiledObjectByName("SPAWN")["position"][:]

        self.worldTextTest = self.CreateEntity("World Text Test",[-150,0],[TextRenderer("World Test String :)", 12, "Arial")])
        self.worldTextTest.GetComponent(TextRenderer).screenSpace = False
        self.screenSpaceText = self.CreateEntity("Screen Text Test",[0,0],[TextRenderer("Screen Text Test", 12, "Arial"),
                                   RectTransformComponent(ALIGN_TOPLEFT,bounds=(0.5,0.1))])
        self.screenSpaceText.GetComponent(TextRenderer).screenSpace = True
        self.screenSpaceText.GetComponent(TextRenderer).SetAlign(ALIGN_TOPLEFT)

        def SpawnEnemyAbovePlayer(s,o):
            if(o.parentEntity.name == "Player") and NetworkState.identity & NET_HOST:
                assets.NetInstantiate("skeleton",self, position=[o.parentEntity.position[0], o.parentEntity.position[1] - 100])

        for i in range(5):
            p = assets.Instantiate("particletest", self)
            p.position = self.GetRandomTiledObjectByName("SPAWN")["position"][:]

        if(self.GetTriggerByName("TEST TRIGGER") != None):
            self.GetTriggerByName("TEST TRIGGER").onTriggerStart.append(SpawnEnemyAbovePlayer)

    def OnDisconnect(self, reason, transportName):
        self.game.LoadScene(self.game._game.startingScene)
        Log(f"Disconnected from server for reason={reason}, transportName={transportName}")