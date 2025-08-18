from sys import platform
import sys
currentPlatform = platform

# Related Python Documentation:
# https://docs.python.org/3.12/library/sys.html#sys.platform

# These functions aren't fully tested on every platform and aren't guaranteed to work.

headless = False

def IsHeadless():
    return headless

def IsPlatformWindows():
    return currentPlatform in ("win32", "cygwin")
def IsPlatformLinux():
    return currentPlatform.startswith("linux")
def IsPlatformMacOS():
    return currentPlatform.startswith("darwin")
def IsPlatformWeb():
    return currentPlatform in ("emscripten", "wasi")

def IsFrozen():
    return getattr(sys, 'frozen', False) #sys.frozen is created by cx_freeze when it's a build
def IsBuilt():
    return IsFrozen() or IsPlatformWeb()
def IsDebug():
    return not IsBuilt()
