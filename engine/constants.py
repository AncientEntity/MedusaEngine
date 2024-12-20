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