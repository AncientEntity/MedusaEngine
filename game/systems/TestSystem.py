from engine.components.rendering.tilemaprenderer import Tilemap, TilemapRenderer
from engine.ecs import EntitySystem, Scene
from engine.scenes.levelscene import LevelScene
from engine.systems.renderer import RenderingSystem


class TestSystem(EntitySystem):
    def __init__(self):
        super().__init__([]) #Put target components here
        self.hoverTileLayer : TilemapRenderer  = None
        self.renderingSystem : RenderingSystem = None
        self.lastPos = (0,0)
    def Update(self,currentScene : Scene):
        tilePos = self.hoverTileLayer.WorldPositionToTileIndex(self.renderingSystem.worldMousePosition)
        self.hoverTileLayer.tileMap.SetTile(-1,self.lastPos[0],self.lastPos[1])
        self.hoverTileLayer.tileMap.SetTile(34,tilePos[0],tilePos[1])
        self.lastPos = tilePos
    def OnEnable(self, currentScene : LevelScene):
        self.hoverTileLayer = currentScene.tileMapLayersByName["Hover"]
        self.renderingSystem = currentScene.GetSystemByClass(RenderingSystem)