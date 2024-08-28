from engine.engine import *
import asyncio

from game import topdowngame
from game.topdowngame import TopdownGame

if __name__ == "__main__":
    gameInstance = Engine(TopdownGame())
    asyncio.run(gameInstance.Start())

