from engine.datatypes.audioclip import AudioClip, GetSound
from engine.ecs import Component
import pygame, time

class AudioPlayer(Component):
    def __init__(self, audioClip : AudioClip, playOnStart=False, volume=1):
        self.clip : AudioClip = None

        self.loops = False # If set to True, the AudioSystem will automatically play it again when it finishes.
        self.destroyOnFinish = False # If true the parent entity will be destroyed on the sound finish playing.

        self.volumeDistanceBased = False
        self._baseVolume = volume

        self._triggerPlay = playOnStart # When set to True, AudioSystem will play it and set this to false.
        self._triggerStop = False # When set to True, AudioSystem will stop audio if it is playing.
        self._playStartTime = 0   # Time at which it started to play

        if(isinstance(audioClip, str) or isinstance(audioClip,  pygame.mixer.Sound)):
            self.clip = AudioClip(audioClip)
        elif(isinstance(audioClip, AudioClip)):
            self.clip = audioClip

    def Play(self):
        self._triggerPlay = True
    def Stop(self):
        self._triggerStop = True
        self._triggerPlay = False

    def IsPlaying(self):
        return time.time() - self._playStartTime <= self.clip.GetSound().get_length()

    def GetSound(self, distance=None, falloffFunc=None):
        sound = GetSound(self.clip)
        if distance is None or not self.volumeDistanceBased:
            sound.set_volume(self._baseVolume)
        elif distance is not None and self.volumeDistanceBased and falloffFunc is not None:
            distanceVolume = self._baseVolume * falloffFunc(distance)
            sound.set_volume(distanceVolume)
        return sound