from engine.components.rendering.spriterenderer import SpriteRenderer
from engine.ecs import Component
from engine.logging import LOG_WARNINGS, Log


class PhysicsComponent(Component):
    def __init__(self,bounds=[10,10],gravity=(0,0)):
        super().__init__()
        self.bounds = bounds #centered on parent entity's position
        self.offset = (0,0)
        self.mapToSpriteOnStart = True
        self.touchingDirections = {'top':  False, 'bottom' : False, 'left' : False, 'right' : False}

        self.physicsLayer = 0
        self.collidesWithLayers = [0]
        self.triggersWithLayers = [0]
        self.onTriggerStart = [] #List of functions that take in body : PhysicsComponent, other : PhysicsComponent. Runs when something 'first starts to trigger with self'

        self.friction = [5,0]
        self.mass = 100.0
        self.static = False #If static it wont be checked in the physics loop as the main body only as other body.
        self.gravity : tuple(float) = gravity #either None or a tuple like: (0,9.84)
        self.velocity = [0,0]

        self._moveRequest = None #Move() adds to this so the physics calculations know what the object wants.
        self._thisStepTriggeredWith = [] #List of other physics components that this collided with this frame.
        self._lastStepTriggeredWith = [] #List of other physics components that this collided with last frame.

        # Spatial Partitioning
        self._overlappingSpatialPartitions = []


    def Move(self,movement):
        if(self._moveRequest == None):
            self._moveRequest = [0,0]
        self._moveRequest[0] += movement[0]
        self._moveRequest[1] += movement[1]

    def AddVelocity(self,impulse):
        self.velocity[0] += impulse[0]
        self.velocity[1] += impulse[1]

    #Makes bounds the same as the sprite's width/height
    def MapToSpriteRenderer(self):
        sR : SpriteRenderer = self.parentEntity.GetComponent(SpriteRenderer)
        if(sR == None):
            Log("Sprite not found when map to sprite renderer. ",LOG_WARNINGS)
            return
        self.bounds = [sR.sprite.get_width(),sR.sprite.get_height()]

    def ResetCollisionDirections(self):
        self.touchingDirections['left'] = False
        self.touchingDirections['right'] = False
        self.touchingDirections['top'] = False
        self.touchingDirections['bottom'] = False

    def IsTouchingDirection(self,direction):
        if(direction == 'down'):
            direction = 'bottom'
        elif(direction == 'up'):
            direction = 'top'
        return self.touchingDirections[direction]