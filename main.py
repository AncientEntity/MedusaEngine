# /// script
# dependencies = [
#  "pygame-ce"
# ]
# ///

from engine.engine import *
import asyncio

from game import bulletgame

if __name__ == "__main__":
    gameInstance = Engine(bulletgame.BulletGame())
    asyncio.run(gameInstance.Start())

