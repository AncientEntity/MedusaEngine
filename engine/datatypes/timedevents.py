import time

class TimedEvent:
    def __init__(self, func, args, startDelay, repeatDelay, repeatCount):
        self.func = func
        self.args = args
        self.startDelay = startDelay
        self.repeatDelay = repeatDelay
        self.repeatCount = repeatCount

        self.creationTime = time.time()
        self.lastRepeatTime = 0
    def Tick(self): # Returns True if it still needs to tick, returns False if it is done.
        if(time.time() - self.creationTime <= self.startDelay):
            return True
        if(time.time() - self.lastRepeatTime <= self.repeatDelay):
            return True


        self.func(*self.args)
        self.lastRepeatTime = time.time()

        self.repeatCount -= 1
        if(self.repeatCount <= 0):
            return False
        return True
    def TimeUntilNextTrigger(self):
        if(self.repeatCount == 0):
            return -1
        cTime = self.startDelay - (time.time() - self.creationTime)
        if(cTime > 0):
            return cTime
        rTime = self.repeatDelay - (time.time() - self.lastRepeatTime)
        return rTime