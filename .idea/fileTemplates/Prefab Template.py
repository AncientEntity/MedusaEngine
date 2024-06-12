from engine.ecs import Scene

def Create${NAME}(scene : Scene):

    newEntity = scene.CreateEntity(name="${NAME}",position=[0,0],components=[])
    return newEntity