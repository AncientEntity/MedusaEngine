from engine.components.audioplayer import AudioPlayer
from engine.ecs import EntitySystem, Scene, Component
import time

from engine.logging import Log


class AudioSystem(EntitySystem):
    def __init__(self):
        super().__init__([AudioPlayer])
        self.audioPlayers = []
    def Update(self,currentScene : Scene):
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
                player.GetSound().play()
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
    def OnDeleteComponent(self, component : Component):
        if(isinstance(component, AudioPlayer)):
            self.audioPlayers.remove(component)