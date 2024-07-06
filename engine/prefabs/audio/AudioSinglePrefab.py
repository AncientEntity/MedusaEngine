from engine.components.audioplayer import AudioPlayer
from engine.ecs import Scene


def CreateAudioSingle(currentScene : Scene, entityName : str, sound, volume):
    player = AudioPlayer(sound,True,volume)
    player.destroyOnFinish = True
    return currentScene.CreateEntity(entityName,[0,0],[player])