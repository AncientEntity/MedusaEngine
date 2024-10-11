from engine.logging import LOG_ERRORS, Log
import pygame

# BaseAsset
# Don't instantiate directly, implement a subclass, then implement LoadAsset which sets self.data
class BaseAsset:
    def __init__(self, fileSource : str):
        self.fileSource = fileSource

        self.isLoaded = False
        self.data = None

        data = assets.RegisterAsset(self)
        if data != None: # If RegisterAsset returns something, it means the asset was already loaded into memory.
            self.data = data
            self.isLoaded = True

    def Get(self):
        if not self.isLoaded:
            self._LoadAsset()
            self.isLoaded = True
        return self.data

    # Loads the asset, implement in subclasses and set self.data
    def LoadAsset(self):
        Log("", LOG_ERRORS)

class SpriteAsset(BaseAsset):
    def __init__(self, fileSource):
        super().__init__(fileSource)
    def LoadAsset(self):
        self.data = pygame.image.load(self.fileSource)

class AssetManager:
    def __init__(self):
        self.assets = {}

    def RegisterAsset(self, asset : BaseAsset):
        if asset.fileSource in self.assets:
            return self.assets[asset.fileSource].data # If asset already loaded, return the asset.
        self.assets[asset.fileSource] = asset
    def UnloadAsset(self):
        pass # todo unloading assets.

assets = AssetManager()