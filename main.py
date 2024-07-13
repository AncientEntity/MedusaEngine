from engine.engine import *
import asyncio

from game.PathfindingGame import PathfindingGame

if __name__ == "__main__":
    gameInstance = Engine(PathfindingGame())
    asyncio.run(gameInstance.Start())

