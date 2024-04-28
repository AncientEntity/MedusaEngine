from datetime import datetime

LOG_NOTHING = 0
LOG_ERRORS = 1
LOG_WARNINGS = 2
LOG_ALL = 3

LOG_LEVEL = 3

def Log(message,level):
    if(LOG_LEVEL >= level):
        print("[Logging]",datetime.now(),":",message)