from engine.debug.debugcollector.debugcollector import DebugCollector
from engine.ecs import Component


class DebugComponent(Component):
    def __init__(self, collector : DebugCollector):
        super().__init__()

        self.collector : DebugCollector = collector