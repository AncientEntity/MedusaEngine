

class Hook():
    def __init__(self):
        self._hookedFuncs = []
    def TriggerHook(self, vals=[]):
        for func in self._hookedFuncs:
            func(*vals)
    def AddHook(self, func):
        self._hookedFuncs.append(func)
    def RemoveHook(self, func):
        self._hookedFuncs.remove(func)
    def ClearHook(self):
        self._hookedFuncs.clear()