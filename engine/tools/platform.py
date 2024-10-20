from sys import platform
currentPlatform = platform

# Related Python Documentation:
# https://docs.python.org/3.12/library/sys.html#sys.platform

# These functions aren't fully tested on every platform and aren't guaranteed to work.

def IsPlatformWindows():
    return currentPlatform in ("win32" or "cygwin")
def IsPlatformLinux():
    return currentPlatform.startswith("linux")
def IsPlatformMacOS():
    return currentPlatform.startswith("darwin")
def IsPlatformWeb():
    return currentPlatform in ("emscripten" or "wasi")