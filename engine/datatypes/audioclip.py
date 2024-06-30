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
        self.sound = None
        if(isinstance(filePathOrSound, str)):
            if(filePathOrSound != ""):
                self.sound = pygame.mixer.Sound(filePathOrSound)
            else:
                self.sound = None
        elif(isinstance(filePathOrSound, pygame.mixer.Sound)):
            self.sound = filePathOrSound
    def GetSound(self):
        return self.sound

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