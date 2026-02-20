# /// script
# dependencies = [
#  "pygame-ce"
# ]
# ///


from engine.engine import *
import asyncio

from game import tinyfactorygame

if __name__ == "__main__":
    gameInstance = Engine(tinyfactorygame.TinyFactoryGame())
    asyncio.run(gameInstance.Start())

