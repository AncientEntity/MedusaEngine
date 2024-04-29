from engine.engine import *
import asyncio

from game import testgame

if __name__ == "__main__":
    gameInstance = Engine(testgame.TestGame())
    asyncio.run(gameInstance.Start())

