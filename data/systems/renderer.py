import pygame.display

from data.ecs import EntitySystem, Scene, Component


class SpriteRenderer(Component):
    def __init__(self, parentEntity, sprite : pygame.Surface):
        super().__init__(parentEntity)
        self.sprite = sprite


class RendererSystem(EntitySystem):
    def __init__(self):
        super().__init__([SpriteRenderer])
    def Update(self,currentScene : Scene):
        currentScene.game.display.fill((255,255,255))

        for spriteRenderer in currentScene.components[SpriteRenderer]:
            if(spriteRenderer.sprite == None):
                continue
            currentScene.game.display.blit(spriteRenderer.sprite,spriteRenderer.parentEntity.position)

        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                currentScene.game.Quit()

        pygame.display.update()