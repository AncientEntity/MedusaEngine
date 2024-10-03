from engine.components.rendering.tilemaprenderer import TilemapRenderer, Tilemap
from engine.ecs import Scene
from engine.systems import renderer
from game import assets


class DungeonScene(Scene):
    def __init__(self):
        super().__init__()
        self.systems.append(renderer.RenderingSystem())
        self.name = "Dungeon Scene"

        self.groundTileMap = Tilemap((200,200))
        self.groundTileMap.tileSize = 16
        self.groundTileMap.SetTileSetFromSpriteSheet(assets.worldTileset)
        for x in range(200):
            for y in range(200):
                import random
                self.groundTileMap.SetTile(random.randint(0,100),x,y)
        self.groundTileRenderer = TilemapRenderer(self.groundTileMap)

        self.CreateEntity("GroundTiles", [0,0], components=[self.groundTileRenderer])
