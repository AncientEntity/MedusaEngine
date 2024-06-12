import random

from engine.scenes.levelscene import LevelScene
from game.components.GeneratorComponent import GeneratorComponent


def CreateGenerator(scene : LevelScene):
    tilePosition = [random.randint(1,14),random.randint(1,14)]
    scene.SetTile(tilePosition,"GeneratorLayer",16)

    newGenerator = scene.CreateEntity("Generator",[tilePosition[0]*16-16*7.5,tilePosition[1]*16-16*8],[GeneratorComponent()])
    return newGenerator