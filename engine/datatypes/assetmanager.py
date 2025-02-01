# todo asset manager
# Instead of storing raw assets (ie pygame.Surfaces) in components it would be better to save a reference
# to an asset here, that gets grabbed whenever it needs to be rendered.
# The current implementation just has things like datatypes.sprites.Sprite holding the surface itself.
# A asset manager instance should be created on start and loaded into the engine instance.
from engine.ecs import Scene
from engine.networking.networkevent import NetworkEvent, NetworkEventCreateEntity
from engine.networking.networkstate import NetworkState


class AssetManager:
    def __init__(self):
        self.prefabs = {}


    def Instantiate(self, prefab_name : str, currentScene : Scene, position=[0,0]):
        entity = currentScene.CreateEntity("",position,[])
        entity.prefabName = prefab_name
        return self.prefabs[prefab_name](entity, currentScene)
    def FactoryInstantiate(self, prefab_name : str):
        def _Instantiate(_currentScene : Scene):
            return self.Instantiate(prefab_name, _currentScene)
        return _Instantiate
    def NetInstantiate(self, prefab_name : str, currentScene : Scene, networkId = None, ownerId = -1, position=[0,0]):
        if ownerId == -1:
            ownerId = NetworkState.clientId

        entity = currentScene.CreateNetworkEntity(prefab_name,position,[], ownerId, networkId)#, Engine._instance.clientId)
        entity.prefabName = prefab_name

        return self.prefabs[prefab_name](entity, currentScene)






assets = AssetManager()