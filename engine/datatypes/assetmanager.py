# todo asset manager
# Instead of storing raw assets (ie pygame.Surfaces) in components it would be better to save a reference
# to an asset here, that gets grabbed whenever it needs to be rendered.
# The current implementation just has things like datatypes.sprites.Sprite holding the surface itself.
# A asset manager instance should be created on start and loaded into the engine instance.