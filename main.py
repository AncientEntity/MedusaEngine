from data.game import *
import asyncio


if __name__ == "__main__":
    gameInstance = Game()
    asyncio.run(gameInstance.Start())

