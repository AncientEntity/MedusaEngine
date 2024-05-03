from datetime import datetime
from sys import exit

LOG_NOTHING = 0
LOG_ERRORS = 1
LOG_WARNINGS = 2
LOG_INFO = 3
LOG_ALL = 4

LOG_LEVEL = 3

def LogPrefix(level):
    if(level == LOG_ALL or level == LOG_INFO):
        return "[Logging]"
    elif(level == LOG_WARNINGS):
        return "[Warning]"
    elif(level == LOG_ERRORS):
        return "[ERROR]"

def Log(message,level):
    if(LOG_LEVEL >= level):
        print(LogPrefix(level),datetime.now(),":",message)
        if(level == LOG_ERRORS):
            raise Exception(message)
            exit(-1)