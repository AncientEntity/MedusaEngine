from engine.components.ui.buttoncomponent import ButtonComponent
from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.components.rendering.textrenderer import TextRenderer
from engine.datatypes.sprites import Sprite
from engine.ecs import Scene
from pygame import Font

def CreateButtonPrefab(scene : Scene, sprite : Sprite, text :str, font : Font):

    spriteRenderer = SpriteRenderer(sprite)
    spriteRenderer.screenSpace = True
    textRenderer = TextRenderer(text, font)
    buttonComponent = ButtonComponent(spriteRenderer,textRenderer)

    newEntity = scene.CreateEntity(name="ButtonPrefab",position=[0,0],components=[buttonComponent,spriteRenderer,textRenderer])
    return newEntity