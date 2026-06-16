from engine.components.audio.audioplayer import AudioPlayer
from engine.ecs import Scene


def CreateAudioSingle(currentScene : Scene, entityName : str, sound, volume, position=None):
    player = AudioPlayer(sound,True,volume)
    player.destroyOnFinish = True
    if position is not None:
        player.volumeDistanceBased = True
    return currentScene.CreateEntity(entityName, position,[player])