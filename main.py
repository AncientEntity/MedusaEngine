from engine.engine import *
import asyncio

from game import jamgame
from game.jamgame import JamGame

if __name__ == "__main__":
    gameInstance = Engine(JamGame())
    asyncio.run(gameInstance.Start())

