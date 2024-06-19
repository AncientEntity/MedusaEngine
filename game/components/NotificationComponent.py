from engine.ecs import Component
import time

class NotificationComponent(Component):
    def __init__(self, startTime):
        super().__init__()
        self.startTime = startTime