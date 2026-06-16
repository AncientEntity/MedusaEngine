from engine.components.audio.audiolistener import AudioListener
from engine.components.audio.audioplayer import AudioPlayer
from engine.ecs import EntitySystem, Scene, Component
import time

from engine.logging import Log, LOG_WARNINGS
from engine.tools.math import Distance


class AudioSystem(EntitySystem):
    def __init__(self):
        super().__init__([AudioPlayer, AudioListener])
        self.removeOnHeadless = True
        self.audioPlayers = []

        self.audioListener : AudioListener = None
    def Update(self,currentScene : Scene):
        listenerPosition = (0,0) if self.audioListener is None else self.audioListener.parentEntity.position

        player : AudioPlayer
        for player in self.audioPlayers:
            isSoundPlaying = player.IsPlaying()

            # Check if sound has finished playing
            if(player._playStartTime > 0 and not isSoundPlaying):
                if(player.loops):
                    player._triggerPlay = True
                elif(player.destroyOnFinish):
                    currentScene.DeleteEntity(player.parentEntity)

            if(player._triggerPlay and not isSoundPlaying):
                if not player.volumeDistanceBased or self.audioListener is None:
                    player.GetSound().play()
                elif self.audioListener is not None:
                    player.GetSound(Distance(player.parentEntity.position, listenerPosition), self.audioListener.falloffFunc).play()
                player._playStartTime = time.time()
                player._triggerPlay = False
            elif(player._triggerStop and isSoundPlaying):
                player.GetSound().stop()
                player._playStartTime = 0

    def OnDisable(self, currentScene : Scene):
        Log(f"AudioSystem({self}) cleaning up")
        for player in self.audioPlayers:
            player.GetSound().stop()
        self.audioPlayers = []

    def OnNewComponent(self,component : Component):
        if(isinstance(component, AudioPlayer)):
            self.audioPlayers.append(component)
        elif(isinstance(component, AudioListener)):
            if self.audioListener is not None:
                Log("Multiple Audio Listener Components found. Taking the newest one.", LOG_WARNINGS)
            self.audioListener = component
            Log("Audio Listener Registered.")
    def OnDeleteComponent(self, component : Component):
        if(isinstance(component, AudioPlayer)):
            self.audioPlayers.remove(component)
        elif(isinstance(component, AudioListener)):
            self.audioListener = None