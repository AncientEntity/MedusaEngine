from engine.constants import KEYDOWN, KEYUP, KEYPRESSED, KEYINACTIVE, INPUT_BIND_FILE
import pygame

from engine.datatypes.inputaction import InputAction
from engine.logging import Log, LOG_INFO, LOG_ALL, LOG_ERRORS, LOG_WARNINGS
from pathlib import Path

from engine.networking.networkstate import NetworkState


class Input:
    _inputStates = {}

    _actions : dict[str,InputAction] = {}
    _actionList : list[InputAction] = []
    _networkActionState : dict[int, bytearray] = {} # clientId, input state bytes

    scroll = 0
    quitPressed = False

    onWindowResized : dict = {} # Dict of functions that get called on pygame.VIDEORESIZE.

    @staticmethod
    def Init(inputActions):
        Input._actions = inputActions
        Input._InitActions()
        Input.LoadBinds()

        # todo implement joysticks
        #joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

    @staticmethod
    def LoadBinds():
        bindPath = Path(INPUT_BIND_FILE)
        if not bindPath.exists():
            bindPath.parent.mkdir(exist_ok=True, parents=True)
            bindFile = open(INPUT_BIND_FILE, 'w')
            bindFile.write(Input.GenerateBindOutput())
            bindFile.close()
            return

        bindFile = open(INPUT_BIND_FILE, 'r')

        for bindLine in bindFile.read().split("\n"):
            if bindLine == "":
                continue
            bindSplit = bindLine.split("=")
            if bindSplit[0] in Input._actions:
                Input._actions[bindSplit[0]].activeBind = int(bindSplit[1])
                Log(f"Bind loaded {bindSplit[0]}, value={bindSplit[1]}", LOG_INFO)
            else:
                Log(f"{bindSplit[0]} not found in actions when loading binds", LOG_WARNINGS)

        bindFile.close()

    @staticmethod
    def _InitActions():
        i = 0
        for name, action in Input._actions.items():
            if "=" in action.name:
                Log(f"Action name {action.name} is invalid, '=' cannot be in the bind name", LOG_ERRORS)
                return
            if name != action.name:
                Log(f"Action key does not match action name", LOG_ERRORS)
            action._id = i
            i += 1
            Input._actionList.append(action)


    @staticmethod
    def GenerateBindOutput():
        output = ""
        for action in Input._actions.values():
            output = f"{output}{action.name}={action.activeBind}\n"
        return output

    @staticmethod
    def ActionStateToBytes():
        actionBytes = bytearray()
        for action in Input._actionList:
            isPressed = KEYPRESSED if Input.ActionPressed(action.name) else KEYINACTIVE
            isDown = KEYDOWN if Input.ActionDown(action.name) else KEYINACTIVE
            isUp = KEYUP if Input.ActionUp(action.name) else KEYINACTIVE
            actionBytes.append(isPressed | isDown | isUp)
        return actionBytes


    @staticmethod
    def InputTick():

        #Go through and mark any KEYDOWN keys as KEYPRESSED and KEYUP keys as inactive.
        for key in Input._inputStates.keys():
            if(Input._inputStates[key] == KEYDOWN):
                Input._inputStates[key] = KEYPRESSED
            elif(Input._inputStates[key] == KEYUP):
                Input._inputStates[key] = KEYINACTIVE

        #Check all the new pygame events for quitting and keys.
        for event in pygame.event.get():
            #Quit Button
            if(event.type == pygame.QUIT):
                Input.quitPressed = True
            #Keys
            elif(event.type == pygame.KEYDOWN):
                Input._inputStates[event.key] = KEYDOWN
            elif(event.type == pygame.KEYUP):
                Input._inputStates[event.key] = KEYUP
            #Scrolling
            elif(event.type == pygame.MOUSEWHEEL):
                Input.scroll = event.y
            #Video Resizing
            elif(event.type == pygame.WINDOWRESIZED):
                Log("WINDOWRESIZED event triggered", LOG_INFO)
                for func in Input.onWindowResized.values():
                    func()

        if NetworkState.clientId != -1:
            Input._networkActionState[NetworkState.clientId] = Input.ActionStateToBytes()

    @staticmethod
    def IsKeyState(key : int, targetState : int) -> bool:
        if(key in Input._inputStates):
            return Input._inputStates[key] == targetState
        else:
            return False #Key Inactive/never recorded.

    @staticmethod
    def KeyPressed(key : int) -> bool:
        return Input.IsKeyState(key,KEYPRESSED) or Input.IsKeyState(key,KEYDOWN)

    @staticmethod
    def KeyDown(key : int) -> bool:
        return Input.IsKeyState(key,KEYDOWN)

    @staticmethod
    def KeyUp(key : int) -> bool:
        return Input.IsKeyState(key,KEYUP)

    @staticmethod
    def ActionPressed(actionName : str, clientId=None) -> bool:
        if not clientId:
            return Input.KeyPressed(Input._actions[actionName].activeBind)
        if clientId not in Input._networkActionState:
            return False
        return Input._networkActionState[clientId][Input._actions[actionName]._id] & KEYPRESSED
    @staticmethod
    def ActionDown(actionName : str, clientId=None) -> bool:
        if not clientId:
            return Input.KeyDown(Input._actions[actionName].activeBind)
        if clientId not in Input._networkActionState:
            return False
        return Input._networkActionState[clientId][Input._actions[actionName]._id] & KEYDOWN
    @staticmethod
    def ActionUp(actionName : str, clientId=None) -> bool:
        if not clientId:
            return Input.KeyUp(Input._actions[actionName].activeBind)
        if clientId not in Input._networkActionState:
            return False
        return Input._networkActionState[clientId][Input._actions[actionName]._id] & KEYUP

    #todo proper mouse inputs (mouse up/down)
    @staticmethod
    def MouseButtonPressed(index):
        return pygame.mouse.get_pressed()[index]

    @staticmethod
    def UpdateNetworkActionState(networkActionState : dict[int, bytearray]):
        for clientId, actionBytes in networkActionState.items():
            if len(actionBytes) == 0: # If no action bytes provided, client disconnected.
                if clientId in Input._networkActionState:
                    Input._networkActionState.pop(clientId)
                continue

            Input._networkActionState[clientId] = actionBytes

    @staticmethod
    def GetNetworkActionState():
        return Input._networkActionState