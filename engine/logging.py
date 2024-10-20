from datetime import datetime
from sys import exit
from pygame import display
import traceback

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

def CreateErrorBox(message):
    stacktrace = "\nTrace\n"
    foundEngine = False
    stack = traceback.format_stack()
    for line in stack[:len(stack)-2]: # exclude last 2 so the last stacktrace is Log

        # Instead of displaying entire stacktrace, find when we reach engine.py then find when we reach asyncio
        # then stop checking.
        if foundEngine and "asyncio" in line:
            break
        if "engine.py" in line:
            foundEngine = True

        stacktrace += line + "\n"

    display.message_box("ERROR", message + stacktrace)

def Log(message,level):
    if(LOG_LEVEL >= level):
        print(LogPrefix(level),datetime.now(),":",message)
        if(level == LOG_ERRORS):
            CreateErrorBox(message)
            raise Exception(message)
            exit(-1)