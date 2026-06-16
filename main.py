# /// script
# dependencies = [
#  "pygame-ce"
# ]
# ///

from engine.engine import *
import asyncio

from game import topdowngame

if __name__ == "__main__":
    gameInstance = Engine(topdowngame.TopdownGame())
    asyncio.run(gameInstance.Start())

