# todo asset manager
# Instead of storing raw assets (ie pygame.Surfaces) in components it would be better to save a reference
# to an asset here, that gets grabbed whenever it needs to be rendered.
# The current implementation just has things like datatypes.sprites.Sprite holding the surface itself.
# A asset manager instance should be created on start and loaded into the engine instance.
from engine.ecs import Scene


class AssetManager:
    def __init__(self):
        self.prefabs = {}


    def Instantiate(self, prefab_name : str, currentScene : Scene):
        return self.prefabs[prefab_name](currentScene)
    def FactoryInstantiate(self, prefab_name : str):
        def _Instantiate(_currentScene : Scene):
            return self.Instantiate(prefab_name, _currentScene)
        return _Instantiate






assets = AssetManager()