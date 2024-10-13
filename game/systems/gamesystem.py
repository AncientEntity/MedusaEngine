import pygame

from engine.components.recttransformcomponent import RectTransformComponent
from engine.components.rendering.particlecomponent import ParticleEmitterComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.components.rendering.textrenderer import TextRenderer
from engine.components.rendering.tilemaprenderer import TilemapRenderer
from engine.components.ui.buttoncomponent import ButtonComponent
from engine.constants import CURSOR_PRESSED, ALIGN_TOPLEFT, ALIGN_BOTTOMLEFT, ALIGN_CENTERLEFT, ALIGN_CENTERRIGHT, \
    ALIGN_CENTERBOTTOM, ALIGN_CENTER, ALIGN_CENTERTOP, ALIGN_TOPRIGHT
from engine.ecs import EntitySystem
from engine.engine import Input
from engine.prefabs.audio.AudioSinglePrefab import CreateAudioSingle
from engine.prefabs.ui.ButtonPrefab import CreateButtonPrefab
from engine.scenes.levelscene import LevelScene
from engine.systems.renderer import RenderingSystem
from game.components.ConsumerComponent import ConsumerComponent
from game.components.GeneratorComponent import GeneratorComponent
from game.components.ItemComponent import ItemComponent
from game.constants import ConveyorPlaceable, UndergroundEntrance, UndergroundExit, worldSpriteSheet, \
    UNDERGROUND_BELT_UNLOCK_LEVEL
from game.datatypes.Placeable import Placeable
from game.prefabs.Generator import CreateGenerator, CreateConsumer
from game.systems.notificationsystem import NotificationSystem


class GameSystem(EntitySystem):
    def __init__(self):
        super().__init__()
        self._tileMapLayer : TilemapRenderer = None
        self._renderer : RenderingSystem = None
        self.previousHoverIndex = (0,0)
        self.placeRotation = 0
        self._money = 160

        self.mainMenu = True
        self.alive = False
        self._level = 1
        self.levelDelay = 15
        self._levelTimeRemaining = self.levelDelay

        self.placeables = [ConveyorPlaceable,UndergroundEntrance,UndergroundExit]
        self.currentlyPlacing : Placeable = self.placeables[0]
    def OnEnable(self, currentScene : LevelScene):
        self.LoadGame(currentScene)

        currentScene.GetSystemByClass(RenderingSystem).backgroundColor = (100,30,30)

        self.mainFont = pygame.font.Font("game/art/PixeloidMono-d94EV.ttf",10)
        self.titleText = pygame.font.Font("game/art/PixeloidMono-d94EV.ttf",20)

        topContainer = RectTransformComponent(ALIGN_CENTERTOP,(0,0),(240,16))
        self.topContainerEnt = currentScene.CreateEntity("UI-TopContainer",(0,0),components=[
            topContainer
        ])

        self.moneyText = TextRenderer("$160",self.mainFont)
        self.moneyText.enabled = False
        self.levelText = TextRenderer("Level: 1",self.mainFont)
        self.levelText.enabled = False
        self.nextOrderText = TextRenderer("Next Order: 20s",self.mainFont)
        self.nextOrderText.enabled = False

        self.moneyTextEnt = currentScene.CreateEntity("MoneyText",[-90,-128],components=[self.moneyText,
                                                      RectTransformComponent(ALIGN_TOPLEFT, (0,0),[60,16],topContainer
                                                                             )])
        self.moneyTextEnt.GetComponent(TextRenderer).SetColor((255,255,255))
        self.moneyTextEnt.GetComponent(TextRenderer).SetAntialiased(False)

        self.levelTextEnt = currentScene.CreateEntity("LevelText",[-30,-128],components=[self.levelText,
                                                     RectTransformComponent(ALIGN_CENTERTOP, (-30,0),[60,16],topContainer)])
        self.levelTextEnt.GetComponent(TextRenderer).SetColor((255,255,255))
        self.levelTextEnt.GetComponent(TextRenderer).SetAntialiased(False)

        self.nextOrderTextEnt = currentScene.CreateEntity("NextOrderText",[65,-128],components=[self.nextOrderText,
                                                          RectTransformComponent(ALIGN_TOPRIGHT, (0,0),[110,16],topContainer)])
        self.nextOrderTextEnt.GetComponent(TextRenderer).SetColor((255,255,255))
        self.nextOrderTextEnt.GetComponent(TextRenderer).SetAntialiased(False)

        self.placementPreviewRenderer = SpriteRenderer(worldSpriteSheet[ConveyorPlaceable.tiles[0]])
        self.placementPreviewRenderer.enabled = False
        self.placementPreviewIcon = currentScene.CreateEntity("PlacementPreviewIcon",[100,118],components=[self.placementPreviewRenderer])

        self.conveyorButton = None
        self.undergroundEntranceButton = None
        self.undergroundExitButton = None

        self._renderer = currentScene.GetSystemByClass(RenderingSystem)
        self._tileMapLayer = currentScene.tileMapLayersObjectsByName["Main"].GetComponent(TilemapRenderer)

        self.creditsText = TextRenderer("Demo game for Medusa Engine", self.mainFont)
        self.creditsText.enabled = True
        self.creditsTextEnt = currentScene.CreateEntity("CreditsText",[0,118],components=[self.creditsText])
        self.creditsText.SetColor((255,255,255))
        self.creditsText.SetAntialiased(False)
        self.creditsText.SetShadow(True,(0,0,0),2)
        currentScene.AddComponent(RectTransformComponent(ALIGN_CENTERBOTTOM,bounds=(200,30)), self.creditsText.parentEntity)

        loseContainerRect = RectTransformComponent(ALIGN_CENTER,(0,-15),(200,150))
        self.loseContainer = currentScene.CreateEntity("UI-LoseContainer", (0,0),components=[
            loseContainerRect
        ])

        self.lostText = TextRenderer("You Lost!", self.titleText)
        self.lostText.enabled = False
        self.lostTextEnt = currentScene.CreateEntity("LostText",[0,-75],components=[self.lostText,
                                                     RectTransformComponent(ALIGN_CENTERTOP,(0,15),(150,30),loseContainerRect)])
        self.lostText.SetColor((255,255,255))
        self.lostText.SetAntialiased(False)
        self.lostText.SetShadow(True,(0,0,0),2)

        self.pressRestartText = TextRenderer("Press Space to Restart", self.mainFont)
        self.pressRestartText.enabled = False
        self.pressRestartTextEnt = currentScene.CreateEntity("RestartText",[0,-30],components=[self.pressRestartText,
                                                           RectTransformComponent(ALIGN_CENTERTOP,(0,55),(150,15),loseContainerRect)])
        self.pressRestartText.SetColor((255,255,255))
        self.pressRestartText.SetAntialiased(False)
        self.pressRestartText.SetShadow(True,(0,0,0),2)

        self.resultLevelText = TextRenderer("Level: 1", self.mainFont)
        self.resultLevelText.enabled = False
        self.resultLevelText.SetAlign(ALIGN_TOPLEFT)
        self.resultLevelTextEnt = currentScene.CreateEntity("resultLevelText",[-80,-10],components=[self.resultLevelText,
                                    RectTransformComponent(ALIGN_BOTTOMLEFT,(0,-58),(45,15),loseContainerRect)])
        self.resultLevelText.SetColor((255,255,255))
        self.resultLevelText.SetAntialiased(False)

        self.resultMoneyText = TextRenderer("Money: 628", self.mainFont)
        self.resultMoneyText.enabled = False
        self.resultMoneyText.SetAlign(ALIGN_TOPLEFT)
        self.resultMoneyTextEnt = currentScene.CreateEntity("resultMoneyText",[-80,5],components=[self.resultMoneyText,
                                    RectTransformComponent(ALIGN_BOTTOMLEFT,(0,-45),(45,15),loseContainerRect)])
        self.resultMoneyText.SetColor((255,255,255))
        self.resultMoneyText.SetAntialiased(False)

        self.resultReasonText = TextRenderer("Reason: Generator Jammed", self.mainFont)
        self.resultReasonText.enabled = False
        self.resultReasonText.SetAlign(ALIGN_TOPLEFT)
        self.resultReasonTextEnt = currentScene.CreateEntity("resultMoneyText",[-80,20],components=[self.resultReasonText,
                                            RectTransformComponent(ALIGN_BOTTOMLEFT,(0,-32),(45,15),loseContainerRect)])
        self.resultReasonText.SetColor((255,255,255))
        self.resultReasonText.SetAntialiased(False)

        mainContainerRect = RectTransformComponent(ALIGN_CENTERTOP,(0,40),(200,64))
        self.mainContainer = currentScene.CreateEntity("UI-MainContainer",(0,0),components=[
            mainContainerRect])

        self.gameTitleText = TextRenderer("Tiny Factory", self.titleText)
        self.gameTitleText.enabled = True
        self.gameTitleTextEnt = currentScene.CreateEntity("Game Title Text",[0,-80],components=[self.gameTitleText,
                                                RectTransformComponent(ALIGN_CENTERTOP,(0,15),(170,20),
                                                                       mainContainerRect)])
        self.gameTitleText.SetColor((255,255,255))
        self.gameTitleText.SetAntialiased(False)
        self.gameTitleText.SetShadow(True,(0,0,0),2)


        self.pressStartText = TextRenderer("Press Space to Start", self.mainFont)
        self.pressStartText.enabled = True
        self.pressStartTextEnt = currentScene.CreateEntity("RestartText",[0,-50],components=[self.pressStartText,
                                                           RectTransformComponent(ALIGN_CENTERTOP,(0,38),(170,20),
                                                                       mainContainerRect)])
        self.pressStartText.SetColor((255,255,255))
        self.pressStartText.SetAntialiased(False)
        self.pressStartText.SetShadow(True,(0,0,0),2)

    def Update(self, currentScene: LevelScene):
        if(not self.alive):
            if Input.KeyDown(pygame.K_SPACE):
                if self.mainMenu:
                    self.StartGame(currentScene)
                else:
                    self.StopGame(currentScene)
                    #self.game.LoadScene(self.game._game.startingScene)
            return

        self.WorldInteraction(currentScene)
        self.Controls()
        self.HandleRound(currentScene)

        if Input.KeyDown(pygame.K_l):
            if not pygame.display.is_fullscreen():
                RenderingSystem.instance.SetResolution(None, True)
            else:
                RenderingSystem.instance.SetResolution((256*2,272*2), False)

    def HandleRound(self,currentScene : LevelScene):
        self.SetLevelTimeRemaining(self._levelTimeRemaining - self.game.deltaTime)
        if(self._levelTimeRemaining <= 0):
            self._level += 1
            self.levelText.SetText("Level: "+str(self._level))
            currentScene.GetSystemByClass(NotificationSystem).CreateNotification(currentScene,
                                                                                 "Level "+str(self._level-1)+ " Completed!")
            self._levelTimeRemaining = self.levelDelay
            CreateGenerator(currentScene)
            if(self._level == UNDERGROUND_BELT_UNLOCK_LEVEL):
                self.UnlockUndergroundBelts(currentScene)

    def StartGame(self, currentScene):
        self.mainMenu = False
        self.ClearMap(currentScene)
        self.alive = True
        self._money = 160
        self.moneyText.SetText("$" + str(self._money))
        self._level = 1

        self.moneyText.enabled = True
        self.levelText.enabled = True
        self.nextOrderText.enabled = True
        self.gameTitleText.enabled = False
        self.pressStartText.enabled = False
        self.creditsText.enabled = False

        CreateGenerator(currentScene)

        self.conveyorButton : ButtonComponent = CreateButtonPrefab(currentScene, worldSpriteSheet[(1,3)], "", self.mainFont).GetComponent(ButtonComponent)
        currentScene.AddComponent(SpriteRenderer(pygame.transform.scale(worldSpriteSheet[6],(8,8)),5,True),
                                    self.conveyorButton.parentEntity)
        self.conveyorButton._anchor = ALIGN_BOTTOMLEFT
        self.conveyorButton._anchorOffset = (15, -12)

    def StopGame(self, currentScene):
        self.mainMenu = True
        self.moneyText.enabled = False
        self.levelText.enabled = False
        self.nextOrderText.enabled = False
        self.gameTitleText.enabled = True
        self.pressStartText.enabled = True
        self.creditsText.enabled = True

        self.lostText.enabled = False
        self.pressRestartText.enabled = False
        self.resultLevelText.enabled = False
        self.resultMoneyText.enabled = False
        self.resultReasonText.enabled = False

    def ClearMap(self, currentScene):

        for generator in currentScene.components[GeneratorComponent][:]:
            currentScene.DeleteEntity(generator.parentEntity)
        for consumer in currentScene.components[ConsumerComponent][:]:
            currentScene.DeleteEntity(consumer.parentEntity)
        for item in currentScene.components[ItemComponent][:]:
            currentScene.DeleteEntity(item.parentEntity)
        for particle in currentScene.components[ParticleEmitterComponent][:]:
            currentScene.DeleteEntity(particle.parentEntity)

        currentScene.ClearTileLayer("HoverLayer")
        currentScene.ClearTileLayer("PreviewLayer")
        currentScene.ClearTileLayer("Objects")
        currentScene.ClearTileLayer("GeneratorLayer")

    def SetLostScreen(self, currentScene : LevelScene, value : bool, reason : str):
        self.alive = not value
        CreateAudioSingle(currentScene, "PlaceSoundSingle", "game/sound/loss.ogg", 1)
        self.creditsText.enabled = value
        self.lostText.enabled = value
        self.pressRestartText.enabled = value
        self.resultLevelText.enabled = value
        self.resultLevelText.SetText("Level: "+str(self._level))
        self.resultMoneyText.enabled = value
        self.resultMoneyText.SetText("Money: "+str(self._money))
        self.resultReasonText.enabled = value
        self.resultReasonText.SetText("Reason: "+reason)

        currentScene.SetTile(self.previousHoverIndex, "PreviewLayer", -1)
        currentScene.SetTile(self.previousHoverIndex, "HoverLayer", -1)
        if self.conveyorButton:
            currentScene.DeleteEntity(self.conveyorButton.parentEntity)
        if(self.undergroundEntranceButton):
            currentScene.DeleteEntity(self.undergroundEntranceButton.parentEntity)
        if(self.undergroundExitButton):
            currentScene.DeleteEntity(self.undergroundExitButton.parentEntity)
        currentScene.DeleteEntity(self.placementPreviewIcon)


    def WorldInteraction(self, currentScene : LevelScene):

        # Uncomment this to save a new main menu.
        #if(Input.KeyDown(pygame.K_t)):
        #    self.SaveGame(currentScene)

        currentHoverIndex = self._tileMapLayer.WorldPointToTileIndexSafe(self._renderer.worldMousePosition)
        if currentHoverIndex != None:
            currentScene.ClearTileLayer("HoverLayer")
            currentScene.SetTile(self.previousHoverIndex,"PreviewLayer",-1)
            self.previousHoverIndex = currentHoverIndex

            #Highlighting and Placing
            if(currentHoverIndex[0] >= 1 and currentHoverIndex[1] >= 1 and currentHoverIndex[0] <= 14 and currentHoverIndex[1] <= 14):
                # Handle special underground belt preview.
                if (self.currentlyPlacing == UndergroundEntrance):
                    self.UndergroundBeltPreview(currentHoverIndex, currentScene, False)
                elif (self.currentlyPlacing == UndergroundExit):
                    self.UndergroundBeltPreview(currentHoverIndex, currentScene, True)

                if(Input.MouseButtonPressed(0)):
                    currentScene.SetTile(currentHoverIndex,"HoverLayer",10)

                    #Attempt place
                    if(currentScene.GetTile(currentHoverIndex,"Objects") == -1 and self._money >= self.currentlyPlacing.cost):
                        self.AddMoney(-self.currentlyPlacing.cost)
                        currentScene.SetTile(currentHoverIndex,"Objects",self.GetPlacingTileIndex())
                        CreateAudioSingle(currentScene, "PlaceSoundSingle", "game/sound/place.ogg", 1)
                elif(Input.MouseButtonPressed(2)):
                    currentScene.SetTile(currentHoverIndex,"HoverLayer",10)
                    if (currentScene.GetTile(currentHoverIndex, "Objects") != -1):
                        currentScene.SetTile(currentHoverIndex,"Objects",-1)
                else:
                    currentScene.SetTile(currentHoverIndex,"HoverLayer",9)
                    currentScene.SetTile(currentHoverIndex,"PreviewLayer", self.GetPlacingTileIndex())

    def Controls(self):
        if(Input.KeyDown(pygame.K_r)):
            self.placeRotation += 1
            self.placementPreviewRenderer.sprite = worldSpriteSheet[self.GetPlacingTileIndex()]
        if(Input.KeyDown(pygame.K_1) or self.conveyorButton.cursorState == CURSOR_PRESSED):
            self.currentlyPlacing = self.placeables[0]
            self.placementPreviewRenderer.sprite = worldSpriteSheet[self.GetPlacingTileIndex()]
        elif(self._level >= UNDERGROUND_BELT_UNLOCK_LEVEL and (Input.KeyDown(pygame.K_2) or self.undergroundEntranceButton.cursorState == CURSOR_PRESSED)):
            self.currentlyPlacing = self.placeables[1]
            self.placementPreviewRenderer.sprite = worldSpriteSheet[self.GetPlacingTileIndex()]
        elif(self._level >= UNDERGROUND_BELT_UNLOCK_LEVEL and (Input.KeyDown(pygame.K_3) or self.undergroundExitButton.cursorState == CURSOR_PRESSED)):
            self.currentlyPlacing = self.placeables[2]
            self.placementPreviewRenderer.sprite = worldSpriteSheet[self.GetPlacingTileIndex()]

    def AddMoney(self,moneyToAdd):
        self._money += moneyToAdd
        self.moneyText.SetText("$"+str(self._money))
    def SetLevelTimeRemaining(self,levelTime):
        self._levelTimeRemaining = levelTime
        self.nextOrderText.SetText("Next Order: "+str(int(self._levelTimeRemaining))+"s")

    def GetPlacingTileIndex(self):
        return self.currentlyPlacing.tiles[self.placeRotation % len(self.currentlyPlacing.tiles)]
    def UndergroundBeltPreview(self,hoverPos,currentScene : LevelScene, reverse):
        lookDirection = (0,0)
        if (self.GetPlacingTileIndex() == UndergroundEntrance.tiles[0] or self.GetPlacingTileIndex() == UndergroundExit.tiles[0]):  # move right
            lookDirection = (1, 0)
        elif(self.GetPlacingTileIndex() == UndergroundEntrance.tiles[1] or self.GetPlacingTileIndex() == UndergroundExit.tiles[1]): #move down
            lookDirection = (0,1)
        elif(self.GetPlacingTileIndex() == UndergroundEntrance.tiles[2] or self.GetPlacingTileIndex() == UndergroundExit.tiles[2]): #move left
            lookDirection = (-1,0)
        elif(self.GetPlacingTileIndex() == UndergroundEntrance.tiles[3] or self.GetPlacingTileIndex() == UndergroundExit.tiles[3]): #move up
            lookDirection = (0,-1)

        if(reverse):
            lookDirection = (-lookDirection[0],-lookDirection[1])

        position = list(hoverPos)
        for i in range(3):
            position[0] += lookDirection[0]
            position[1] += lookDirection[1]
            if(position[0] < 1 or position[0] > 14):
                return
            if(position[1] < 1 or position[1] > 14):
                return
            currentScene.SetTile(position, "HoverLayer", 9, True)
    def UnlockUndergroundBelts(self, currentScene): # I don't like this solution but for a remake/example game it's not an issue.

        self.undergroundEntranceButton : ButtonComponent = CreateButtonPrefab(currentScene, worldSpriteSheet[(1,3)], "", self.mainFont).GetComponent(ButtonComponent)
        currentScene.AddComponent(SpriteRenderer(pygame.transform.scale(worldSpriteSheet[2], (8, 8)), 5,True),
                                  self.undergroundEntranceButton.parentEntity)
        self.undergroundEntranceButton._anchor = ALIGN_BOTTOMLEFT
        self.undergroundEntranceButton._anchorOffset = (35, -12)

        self.undergroundExitButton : ButtonComponent = CreateButtonPrefab(currentScene, worldSpriteSheet[(1,3)], "", self.mainFont).GetComponent(ButtonComponent)
        currentScene.AddComponent(SpriteRenderer(pygame.transform.scale(worldSpriteSheet[3], (8, 8)), 5,True),
                                  self.undergroundExitButton.parentEntity)
        self.undergroundExitButton._anchor = ALIGN_BOTTOMLEFT
        self.undergroundExitButton._anchorOffset = (55, -12)

        currentScene.GetSystemByClass(NotificationSystem).CreateNotification(currentScene, "Underground Belts Unlocked!")

    def SaveGame(self, currentScene : LevelScene):
        import pickle

        objLayerFile = open("game/data/objlayer.dat","wb")
        genLayerFile = open("game/data/genlayer.dat","wb")
        consumerFile = open("game/data/consumers.dat","wb")
        generatorFile = open("game/data/generators.dat","wb")

        pickle.dump(currentScene.tileMapLayersByName["Objects"].tileMap.map,objLayerFile)
        pickle.dump(currentScene.tileMapLayersByName["GeneratorLayer"].tileMap.map,genLayerFile)

        consumers = []
        consumer : ConsumerComponent
        for consumer in currentScene.components[ConsumerComponent]:
            consumers.append((consumer.parentEntity.position, consumer.itemID))
        pickle.dump(consumers, consumerFile)
        generators = []
        generator : GeneratorComponent
        for generator in currentScene.components[GeneratorComponent]:
            generators.append((generator.parentEntity.position,generator.itemID))
        pickle.dump(generators, generatorFile)

        objLayerFile.close()
        genLayerFile.close()
        consumerFile.close()
        generatorFile.close()
        print("Saved Main Menu")
    def LoadGame(self, currentScene : LevelScene):
        import pickle
        currentScene.tileMapLayersByName["Objects"].tileMap.map = pickle.load(open("game/data/objlayer.dat","rb"))
        currentScene.tileMapLayersByName["GeneratorLayer"].tileMap.map = pickle.load(open("game/data/genlayer.dat","rb"))
        consumers = pickle.load(open("game/data/consumers.dat","rb"))
        for consumer in consumers:
            CreateConsumer(currentScene,consumer[1],consumer[0])
        generators = pickle.load(open("game/data/generators.dat","rb"))
        for generator in generators:
            CreateGenerator(currentScene,generator[1],generator[0])

        print("Loaded Main Menu")