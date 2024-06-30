import pygame

# todo this is pretty basic at the moment, eventually I want ConditionalAudioClip, RandomAudioClip, etc
# todo which would function similarly to how AnimatedSprites work and such, where we use a GetClip function
# todo which determines which audio clip we want to play, allowing for nested audio clips and more complex behaviour.

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