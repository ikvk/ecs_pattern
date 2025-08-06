import os

import pygame
from pygame import DOUBLEBUF, FULLSCREEN, SCALED
from pygame.time import Clock

from common_tools.consts import (
    GAME_NAME,
    GAME_VERSION,
    SCREEN_HEIGHT_PX,
    SCREEN_WIDTH_PX,
    SETTING_SCREEN_MODE_FULL,
    SETTINGS_STORAGE,
    SURFACE_ARGS,
)
from fall.main import game_loop
from menu.main import menu_loop

os.environ['SDL_VIDEO_CENTERED'] = '1'  # window at center


def main():
    """Точка входа в приложение"""
    # NOTE: pygame.init() в common_tools.consts
    pygame.display.set_caption(f'{GAME_NAME} {GAME_VERSION}')
    is_fullscreen = SETTINGS_STORAGE.screen_mode == SETTING_SCREEN_MODE_FULL
    display = pygame.display.set_mode(
        size=(SCREEN_WIDTH_PX, SCREEN_HEIGHT_PX),
        flags=(FULLSCREEN | SCALED if is_fullscreen else 0) | DOUBLEBUF,
        depth=SURFACE_ARGS['depth']
    )
    clock = Clock()

    while True:
        menu_loop(display, clock)
        game_loop(display, clock)


if __name__ == '__main__':
    main()
