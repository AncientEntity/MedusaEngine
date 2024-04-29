from engine.engine import *
import asyncio

from game.testing import testgame

if __name__ == "__main__":
    gameInstance = Engine(testgame.TestGame())
    asyncio.run(gameInstance.Start())

