from engine.components.rendering.tilemaprenderer import Tilemap, TilemapRenderer
from engine.datatypes.pathfinding import TilemapPathfinder
from engine.ecs import EntitySystem, Scene
from engine.engine import Input
from engine.scenes.levelscene import LevelScene
from engine.systems.renderer import RenderingSystem


class TestSystem(EntitySystem):
    def __init__(self):
        super().__init__([]) #Put target components here
        self.hoverTileLayer : TilemapRenderer  = None
        self.pathTileLayer : TilemapRenderer  = None
        self.renderingSystem : RenderingSystem = None
        self.lastPos = (0,0)

        self.startPos = None
        self.endPos = None

        self.pathfinding : TilemapPathfinder = None
    def Update(self,currentScene : Scene):
        tilePos = self.hoverTileLayer.WorldPositionToTileIndex(self.renderingSystem.worldMousePosition)
        if(tilePos == self.startPos):
            return
        if(self.lastPos != self.startPos and self.lastPos != self.endPos):
            self.hoverTileLayer.tileMap.SetTile(-1,self.lastPos[0],self.lastPos[1])
            self.hoverTileLayer.tileMap.SetTile(34,tilePos[0],tilePos[1])
        self.lastPos = tilePos
        if (Input.MouseButtonPressed(0)):
            if(self.startPos != None):
                self.hoverTileLayer.tileMap.SetTile(-1, self.startPos[0], self.startPos[1])
            self.startPos = tilePos
            self.hoverTileLayer.tileMap.SetTile(419, self.startPos[0], self.startPos[1])
        if (Input.MouseButtonPressed(2)):
            if(self.endPos != None):
                self.hoverTileLayer.tileMap.SetTile(-1, self.endPos[0], self.endPos[1])
            self.endPos = tilePos
            self.hoverTileLayer.tileMap.SetTile(417, self.endPos[0], self.endPos[1])
        if(self.startPos != None and self.endPos != None):
            self.pathTileLayer.tileMap.Clear()
            path = self.pathfinding.Solve(self.startPos,self.endPos)
            if(path != None):
                for index in path:
                    self.pathTileLayer.tileMap.SetTile(418,index[0],index[1])

    def OnEnable(self, currentScene : LevelScene):
        self.hoverTileLayer = currentScene.tileMapLayersByName["Hover"]
        self.pathTileLayer = currentScene.tileMapLayersByName["Path"]
        self.renderingSystem = currentScene.GetSystemByClass(RenderingSystem)
        self.pathfinding = TilemapPathfinder(list(currentScene.tileMapLayersByName.values()), [0], True)