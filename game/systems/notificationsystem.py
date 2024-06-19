from engine.components.rendering.textrenderer import TextRenderer
from engine.ecs import EntitySystem, Scene, Component, Entity
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
        for notification in self.notifications[:]:
            timeLeft = time.time() - notification.GetComponent(NotificationComponent).startTime
            if(timeLeft <= 0):
                self.notifications.remove(notification)
                continue

            notification.position[1] = 97 - index*10
            notification.GetComponent(TextRenderer).SetAlpha(255-255*(timeLeft/self.halfLife))
            index += 1
    def OnEnable(self, currentScene : Scene):
        self.notificationFont = pygame.font.Font("game/art/PixeloidMono-d94EV.ttf",10)
        self.CreateNotification(currentScene, "Test Notification!")

    def CreateNotification(self, currentScene : LevelScene, text):
        textRenderer = TextRenderer(text,self.notificationFont)
        textRenderer.screenSpace = True
        textRenderer.drawOrder = 1000
        textRenderer.SetColor((255,255,255))
        notifyEntity = currentScene.CreateEntity("Notification",[-48,97],[textRenderer, NotificationComponent()])

        self.notifications.append(notifyEntity)