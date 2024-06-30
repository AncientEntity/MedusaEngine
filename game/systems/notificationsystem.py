from engine.components.rendering.textrenderer import TextRenderer
from engine.constants import ALIGN_TOPLEFT
from engine.ecs import EntitySystem, Scene, Component, Entity
from engine.prefabs.audio.AudioSinglePrefab import CreateAudioSingle
from engine.scenes.levelscene import LevelScene
import pygame
import time
from game.components.NotificationComponent import NotificationComponent


class NotificationSystem(EntitySystem):
    def __init__(self):
        super().__init__([]) #Put target components here
        self.notifications = []

        self.notificationFont = None
        self.halfLife = 3.0

    def Update(self,currentScene : Scene):
        index = 0
        notification : Entity
        for notification in self.notifications[::-1]:
            timeLeft = self.halfLife - (time.time() - notification.GetComponent(NotificationComponent).startTime)
            if(timeLeft <= 0):
                currentScene.DeleteEntity(notification)
                self.notifications.remove(notification)
                continue

            notification.position[1] = 90 - index*11
            notification.GetComponent(TextRenderer).SetAlpha(350*(timeLeft/self.halfLife)) #Alpha above 255 so it doesn't immediately start disappearing.
            index += 1
    def OnEnable(self, currentScene : Scene):
        self.notificationFont = pygame.font.Font("game/art/PixeloidMono-d94EV.ttf",10)

    def CreateNotification(self, currentScene : LevelScene, text):
        textRenderer = TextRenderer(text,self.notificationFont)
        textRenderer.screenSpace = True
        textRenderer.drawOrder = 1000
        textRenderer.SetColor((255,255,255))
        textRenderer.SetAlign(ALIGN_TOPLEFT)
        notifyEntity = currentScene.CreateEntity("Notification",[-110,90],[textRenderer, NotificationComponent(time.time())])

        self.notifications.append(notifyEntity)
        CreateAudioSingle(currentScene, "PlaceSoundSingle", "game/sound/notificationsound.ogg", 1)
        return notifyEntity