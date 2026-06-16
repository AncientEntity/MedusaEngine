import pygame, random

def GetSound(audioClip, getTailSound=False):
    if(isinstance(audioClip,pygame.mixer.Sound)):
        return audioClip
    else:
        nextClip = audioClip.GetSound()
        if(getTailSound == True and isinstance(nextClip,pygame.mixer.Sound)):
            return audioClip
        return nextClip

class AudioClip:
    def __init__(self, filePathOrSound : str or pygame.mixer.Sound):
        self.filePathOrSound = filePathOrSound
        self.sound = None

    def GetSound(self):
        if self.sound is None:
            self._LoadSound()

        return self.sound
    def _LoadSound(self):
        if(isinstance(self.filePathOrSound, str)):
            if(self.filePathOrSound != ""):
                self.sound = pygame.mixer.Sound(self.filePathOrSound)
            else:
                self.sound = None
        elif(isinstance(self.filePathOrSound, pygame.mixer.Sound)):
            self.sound = self.filePathOrSound

class RandomAudioClip(AudioClip):
    def __init__(self, sounds):
        self.sounds = []
        for clip in sounds:
            self.sounds.append(AudioClip(clip))
        self.sound = GetSound(self.sounds[0])
    def GetSound(self):
        randomSound = GetSound(random.choice(self.sounds))
        self.sound = randomSound
        return randomSound