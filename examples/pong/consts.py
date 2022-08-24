class Team:
    LEFT = 1
    RIGHT = 2
    names = (
        (LEFT, "Left"),
        (RIGHT, "Right"),
    )
    values = (LEFT, RIGHT)


FPS_MAX = 100
FPS_CORR = 24 / FPS_MAX

BALL_SIZE = 0.03  # relative to screen height
BALL_SPEED_MIN = 0.02 * FPS_CORR  # relative to screen height

RACKET_WIDTH = BALL_SIZE
RACKET_HEIGHT = 0.22  # relative to screen height
RACKET_SPEED = 0.03 * FPS_CORR  # relative to screen height
