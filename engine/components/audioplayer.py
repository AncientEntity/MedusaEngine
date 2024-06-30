from engine.datatypes.audioclip import AudioClip, GetSound
from engine.ecs import Component
import pygame, time

class AudioPlayer(Component):
    def __init__(self, audioClip : AudioClip, playOnStart=False, volume=1):
        self.clip : AudioClip = None

        self.loops = False # If set to True, the AudioSystem will automatically play it again when it finishes.
        self.destroyOnFinish = False # If true the parent entity will be destroyed on the sound finish playing.

        self._volume = volume

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
        return time.time() - self._playStartTime <= self.clip.sound.get_length()

    def GetSound(self):
        sound = GetSound(self.clip)
        sound.set_volume(self._volume)
        return sound