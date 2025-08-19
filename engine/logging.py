from datetime import datetime
from sys import exit
from pygame import display
import traceback
import os

import engine.tools.platform
from engine.tools.platform import IsPlatformWeb, IsDebug

# Log Constants
LOG_NOTHING = 0
LOG_ERRORS = 1
LOG_WARNINGS = 2
LOG_INFO = 3
LOG_ALL = 4

LOG_NETWORKING = 2.1
LOG_NETWORKPROCESS = 3.1

# Log Settings
LOG_LEVEL = LOG_INFO
MAX_LOG_FILES = 10

# Controls how often Log() will flush the log file's buffer.
FILE_FLUSH_THRESHOLD = 20 if IsDebug() else None # When set to None, no manual flushing occurs.
_FILE_LOG_COUNT = 0
lastLogFile = None


def LogPrefix(level):
    if(level == LOG_ALL or level == LOG_INFO):
        return "[Logging]"
    elif(level == LOG_WARNINGS):
        return "[Warning]"
    elif(level == LOG_ERRORS):
        return "[ERROR]"
    elif (level == LOG_NETWORKING):
        return "[NET]"
    elif(level == LOG_NETWORKPROCESS):
        return "[NETPROCESS]"

def CreateErrorBox(message):
    if engine.tools.platform.headless:
        return

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

def Log(message,level=LOG_INFO):
    global _FILE_LOG_COUNT
    if(LOG_LEVEL >= level):
        output = f"{LogPrefix(level)} {datetime.now()} {message}"
        print(output)

        if lastLogFile:
            lastLogFile.write(output+"\n")
            if FILE_FLUSH_THRESHOLD != None:
                _FILE_LOG_COUNT += 1
                if _FILE_LOG_COUNT % FILE_FLUSH_THRESHOLD == 0:
                    _FILE_LOG_COUNT = 0
                    lastLogFile.flush()

        if(level == LOG_ERRORS):
            CreateErrorBox(message)
            raise Exception(message)
            exit(-1)

logFileName = datetime.now().strftime("logging/log-%Y-%m-%d_%H-%M-%S.log")
if not IsPlatformWeb():
    if not os.path.exists("logging"):
        os.mkdir("logging")

    lastLogFile = open(logFileName, "a")

    existingLogFiles = os.listdir("logging")
    validLogCount = len(existingLogFiles)
    if (validLogCount >= MAX_LOG_FILES + 1):
        oldestFile = None
        oldestFileTime = None
        for existingLog in existingLogFiles:
            try:
                timeCreated = datetime.strptime(existingLog, "log-%Y-%m-%d_%H-%M-%S.log")
            except ValueError:
                validLogCount -= 1
                continue # whatever file is in logging doesnt match the regex of strptime.
            if oldestFileTime == None or timeCreated < oldestFileTime:
                oldestFile = existingLog
                oldestFileTime = timeCreated
        if validLogCount >= MAX_LOG_FILES + 1:
            os.remove("logging/"+oldestFile)
            Log(f"Removed old log {oldestFile}", LOG_INFO)

    # todo I have decided overriding excepthook is alright for now
    # todo in the future it should be changed to python's logging library.
    import sys, atexit
    defaultExceptHook = sys.excepthook
    def MedusaExceptHook(type, value, trace):
        formattedTrace = ""
        for line in traceback.format_tb(trace):
            formattedTrace += line

        Log(f"Exception Caught: {type}, {value}, {formattedTrace}", LOG_ERRORS)
        lastLogFile.close()
        defaultExceptHook(type,value,trace)
    sys.excepthook = MedusaExceptHook

    def OnRegularExit():
        Log("Closing Log File", LOG_INFO)
        if lastLogFile and not lastLogFile.closed:
            lastLogFile.close()
    atexit.register(OnRegularExit)