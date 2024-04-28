import pygame

from data import ecs
from data.systems import renderer
from data.systems.renderer import SpriteRenderer

TestScene = ecs.Scene()
TestScene.systems.append(renderer.RendererSystem())
ent = ecs.Entity()
TestScene.entities.append(ent)
ent.position = [500, 500]
t = SpriteRenderer(ent, pygame.image.load("data/art/testplayer.png"))
TestScene.AddComponent(t)