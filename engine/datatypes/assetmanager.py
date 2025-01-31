# todo asset manager
# Instead of storing raw assets (ie pygame.Surfaces) in components it would be better to save a reference
# to an asset here, that gets grabbed whenever it needs to be rendered.
# The current implementation just has things like datatypes.sprites.Sprite holding the surface itself.
# A asset manager instance should be created on start and loaded into the engine instance.
from engine.ecs import Scene
from engine.networking.networkevent import NetworkEvent, NetworkEventCreateEntity


class AssetManager:
    def __init__(self):
        self.prefabs = {}


    def Instantiate(self, prefab_name : str, currentScene : Scene, position=[0,0]):
        entity = currentScene.CreateEntity("",position,[])
        return self.prefabs[prefab_name](entity, currentScene)
    def FactoryInstantiate(self, prefab_name : str):
        def _Instantiate(_currentScene : Scene):
            return self.Instantiate(prefab_name, _currentScene)
        return _Instantiate
    def NetInstantiate(self, prefab_name : str, currentScene : Scene, position=[0,0]):
        entity = currentScene.CreateNetworkEntity("",position,[])#, Engine._instance.clientId)

        createEvent = NetworkEventCreateEntity(prefab_name, position)
        #Engine._instance._networkSendQueue.append(NetworkEvent(NET_EVENT_ENTITY_CREATE,
        #                                                       createEvent.ToBytes()))

        return self.prefabs[prefab_name](entity, currentScene)






assets = AssetManager()