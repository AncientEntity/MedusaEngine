from engine.constants import KEYDOWN, KEYUP, KEYPRESSED, KEYINACTIVE
import pygame

from engine.logging import Log, LOG_INFO, LOG_ALL


class Input:
    _inputStates = {}

    scroll = 0
    quitPressed = False

    onWindowResized : dict = {} # Dict of functions that get called on pygame.VIDEORESIZE.

    @staticmethod
    def Init():
        joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        print(joysticks)

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


    #todo proper mouse inputs (mouse up/down)
    @staticmethod
    def MouseButtonPressed(index):
        return pygame.mouse.get_pressed()[index]
