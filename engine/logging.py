from datetime import datetime

LOG_NOTHING = 0
LOG_ERRORS = 1
LOG_WARNINGS = 2
LOG_ALL = 3

LOG_LEVEL = 3

def LogPrefix(level):
    if(level == 3):
        return "[Logging]"
    elif(level == 2):
        return "[Warning]"
    elif(level == 1):
        return "[ERROR]"

def Log(message,level):
    if(LOG_LEVEL >= level):
        print(LogPrefix(level),datetime.now(),":",message)