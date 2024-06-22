import random

from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.scenes.levelscene import LevelScene
from game.components.ConsumerComponent import ConsumerComponent
from game.components.GeneratorComponent import GeneratorComponent
from game.prefabs.Item import itemSpriteSheet


def CreateGenerator(scene : LevelScene):
    tilePosition = [random.randint(1,14),random.randint(1,14)]
    attempts = 50
    while(scene.GetTile(tilePosition,"GeneratorLayer") != -1 or scene.GetTile(tilePosition,"Objects") != -1):
        tilePosition = [random.randint(1, 14), random.randint(1, 14)]
        attempts -= 1
        if(attempts <= 0):
            continue

    scene.SetTile(tilePosition,"GeneratorLayer",16)

    targetItem = random.randint(0,12)

    CreateConsumer(scene,targetItem)

    newGenerator = scene.CreateEntity("Generator",[tilePosition[0]*16-16*7.5,tilePosition[1]*16-16*8],[GeneratorComponent(targetItem)])
    return newGenerator

def CreateConsumer(scene : LevelScene, wantedItem):
    tilePosition = [random.randint(1,14),random.randint(1,14)]
    attempts = 50
    while(scene.GetTile(tilePosition,"GeneratorLayer") != -1 or scene.GetTile(tilePosition,"Objects") != -1):
        tilePosition = [random.randint(1, 14), random.randint(1, 14)]
        attempts -= 1
        if(attempts <= 0):
            continue

    scene.SetTile(tilePosition,"GeneratorLayer",24)

    newConsumer = scene.CreateEntity("Consumer",[tilePosition[0]*16-16*7.5,tilePosition[1]*16-16*8],[ConsumerComponent(wantedItem),
                                                                                                     SpriteRenderer(itemSpriteSheet[wantedItem])])
    newConsumer.GetComponent(SpriteRenderer).sprite.SetAlpha(80)
    return newConsumer