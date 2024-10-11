import time

class TimedEvent:
    def __init__(self, func, args, startDelay, repeatDelay, repeatCount):
        self.func = func
        self.args = args
        self.startDelay = startDelay
        self.repeatDelay = repeatDelay
        self.repeatCount = repeatCount # If set to None, it repeats forever.

        self.creationTime = time.time()
        self.lastRepeatTime = 0
    def Tick(self): # Returns True if it still needs to tick, returns False if it is done.
        if(time.time() - self.creationTime <= self.startDelay):
            return True
        if(time.time() - self.lastRepeatTime <= self.repeatDelay):
            return True


        self.func(*self.args)
        self.lastRepeatTime = time.time()

        # Reduce repeats left, if repeatCount is None, it repeats forever.
        if self.repeatCount != None:
            self.repeatCount -= 1
            if(self.repeatCount <= 0):
                return False

        return True
    def TimeUntilNextTrigger(self, curTime):
        if(self.repeatCount == 0):
            return -1
        cTime = self.startDelay - (curTime - self.creationTime)
        if(cTime > 0):
            return cTime
        rTime = self.repeatDelay - (curTime - self.lastRepeatTime)
        return rTime