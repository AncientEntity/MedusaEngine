import engine.logging
from engine.logging import Log

# Good Reference: https://developer.mozilla.org/en-US/docs/Web/API/Window

if engine.tools.platform.IsPlatformWeb():
    from platform import window
    def GetCookie(cookieName, defaultValue): #todo ability to GetCookieAsValue or something
        cookieValue = window.localStorage.getItem(cookieName)
        return cookieValue if cookieValue is not None else defaultValue
    def SetCookie(cookieName, newValue): # todo ability to SetCookieAsValue or something
        window.localStorage.setItem(cookieName, newValue)
    def DeleteCookie(cookieName):
        window.localStorage.removeItem(cookieName)
    def DeleteAllCookies():
        for i in range(window.localStorage.length):
            window.localStorage.removeItem(window.localStorage.key(i))

else:
    def GetCookie(cookieName, defaultValue):
        Log("Cannot GetCookie on non web platform...")
    def SetCookie(cookieName, newValue):
        Log("Cannot SetCookie on non web platform...")
    def DeleteCookie(cookieName):
        Log("Cannot DeleteCookie on non web platform...")
    def DeleteAllCookies():
        Log("Cannot DeleteAllCookies on non web platform...")
