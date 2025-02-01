# List of engine constants, don't put game constants here

# ----------------------------------------
# INPUT CONSTANTS
# ----------------------------------------
KEYINACTIVE = 0  # When input/key has no state
KEYPRESSED = 1  # When input/key is actively being pressed
KEYDOWN = 2  # When input/key is pressed down (for 1 frame)
KEYUP = 3  # When input/key is released (for 1 frame)

# ----------------------------------------
# UI CONSTANTS
# ----------------------------------------
CURSOR_NONE = 0 # When cursor isn't hovering or clicking a UI element
CURSOR_HOVERING = 1 # When cursor is hovering over a UI element
CURSOR_PRESSED = 2 # When cursor is pressed on a UI element

ALIGN_NONE = None
ALIGN_CENTER = 0
ALIGN_CENTERLEFT = 1
ALIGN_CENTERRIGHT = 2
ALIGN_TOPLEFT = 3
ALIGN_TOPRIGHT = 4
ALIGN_BOTTOMLEFT = 5
ALIGN_BOTTOMRIGHT = 6
ALIGN_CENTERBOTTOM = 7
ALIGN_CENTERTOP = 8

# ----------------------------------------
# SPLASH CONSTANTS
# ----------------------------------------
SPLASH_DISABLED = 0 # No Splash
SPLASH_ALWAYS = 1 # Always Show Splash
SPLASH_BUILDONLY = 2 # Only show splash in build, not debug mode.

# ----------------------------------------
# NETWORK CONSTANTS
# ----------------------------------------
NET_TICKRATE = 64
NET_SNAPSHOT_RATE = 20

NET_EVENT_NONE = 0
NET_EVENT_INIT = 1
NET_EVENT_SNAPSHOT_PARTIAL = 2
NET_EVENT_SNAPSHOT_FULL = 3

NET_NONE = 0b0
NET_CLIENT = 0b01
NET_HOST = 0b10
NET_LISTENSERVER = NET_CLIENT | NET_HOST

NET_SNAPSHOT_PARTIAL = 2
NET_SNAPSHOT_FULL = 3

NET_PROCESS_UNKNOWN = 0
NET_PROCESS_SHUTDOWN = 1
NET_PROCESS_OPEN_SERVER_TRANSPORT = 2
NET_PROCESS_CLOSE_SERVER_TRANSPORT = 3
NET_PROCESS_CONNECT_CLIENT_TRANSPORT = 4
NET_PROCESS_CLOSE_CLIENT_TRANSPORT = 5
NET_PROCESS_CLIENT_SEND_MESSAGE = 6
NET_PROCESS_SERVER_SEND_MESSAGE = 7
NET_PROCESS_RECEIVE_MESSAGE = 8