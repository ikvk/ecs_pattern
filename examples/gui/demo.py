import os

import pygame
from pygame import DOUBLEBUF, FULLSCREEN, SCALED
from pygame.time import Clock

from common_tools.consts import (
    SCREEN_HEIGHT_PX,
    SCREEN_WIDTH_PX,
    SURFACE_ARGS,
)
from demo.main import demo_loop

os.environ['SDL_VIDEO_CENTERED'] = '1'  # window at center


def main():
    """Точка входа в приложение"""
    # NOTE: pygame.init() в common_tools.consts
    pygame.display.set_caption('gui demo')
    is_fullscreen = False
    display = pygame.display.set_mode(
        size=(SCREEN_WIDTH_PX, SCREEN_HEIGHT_PX),
        flags=(FULLSCREEN | SCALED if is_fullscreen else 0) | DOUBLEBUF,
        depth=SURFACE_ARGS['depth']
    )
    clock = Clock()

    while True:
        demo_loop(display, clock)


if __name__ == '__main__':
    main()
