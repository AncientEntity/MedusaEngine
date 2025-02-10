

class InputAction:
    def __init__(self, name : str, defaultBind, networked=False):
        self.name = name

        self.defaultBind = defaultBind
        self.activeBind = self.defaultBind #110

