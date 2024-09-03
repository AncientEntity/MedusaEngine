from engine.ecs import Component

class ItemComponent(Component):
    def __init__(self):
        super().__init__()

        self.owningActor = None

        # Rendering
        self.spriteRotationOffset = 0
        self.spriteRotateHalf = False # If true, instead of fully rotating it will FlipY, so it will turn in the other
                                      # direction. Prevents unsymmetry weapons (ex: slingshot) from rotating upsidedown.

    @property
    def held(self):
        return self.owningActor is not None
