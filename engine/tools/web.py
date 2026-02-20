import engine.logging
from engine.logging import Log

# Good Reference: https://developer.mozilla.org/en-US/docs/Web/API/Window

if engine.tools.platform.IsPlatformWeb():
    from platform import window
    def GetLocalStorage(cookieName, defaultValue, returnType = str):
        cookieValue = window.localStorage.getItem(cookieName)
        if cookieValue is None:
            return defaultValue

        if (isinstance(returnType, str) and returnType[0:4] == "list") or isinstance(returnType, list):
            valuesType = returnType[4:] if isinstance(returnType, str) else None
            vec = []
            for val in cookieValue.split("|"):
                valCasted = val
                if valuesType == "int":
                    valCasted = int(valCasted)
                elif valuesType == "float":
                    valCasted = float(valCasted)
                vec.append(valCasted)
            return vec
        else:
            return cookieValue

    def SetLocalStorage(cookieName, newValue):
        if isinstance(newValue, list):
            stringVector = ""
            for v in newValue:
                stringVector += str(v) + "|"
            window.localStorage.setItem(cookieName,stringVector[:-1]) # Ignore last "|"
        else:
            window.localStorage.setItem(cookieName, newValue)

    def DeleteLocalStorage(cookieName):
        window.localStorage.removeItem(cookieName)
    def DeleteAllLocalStorage():
        for i in range(window.localStorage.length):
            window.localStorage.removeItem(window.localStorage.key(i))

else:
    def GetLocalStorage(cookieName, defaultValue, returnType):
        Log("Cannot GetLocalStorage on non web platform...", engine.LOG_WARNINGS)
    def SetLocalStorage(cookieName, newValue):
        Log("Cannot SetLocalStorage on non web platform...", engine.LOG_WARNINGS)
    def DeleteLocalStorage(cookieName):
        Log("Cannot DeleteLocalStorage on non web platform...", engine.LOG_WARNINGS)
    def DeleteAllLocalStorage():
        Log("Cannot DeleteAllLocalStorage on non web platform...", engine.LOG_WARNINGS)