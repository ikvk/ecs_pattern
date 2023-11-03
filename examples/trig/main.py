import os

import pygame
from pygame import FULLSCREEN, DOUBLEBUF, SCALED
from pygame.time import Clock

from common_tools.consts import SCREEN_WIDTH, SCREEN_HEIGHT, SURFACE_ARGS, SETTING_SCREEN_MODE_FULL, SETTINGS_STORAGE
from fall.main import game_loop
from menu.main import menu_loop

os.environ['SDL_VIDEO_CENTERED'] = '1'  # window at center


def main():
    """Точка входа в приложение"""
    # pygame.init() в common_tools.consts
    pygame.display.set_caption('Trig FALL')
    is_fullscreen = SETTINGS_STORAGE.screen_mode == SETTING_SCREEN_MODE_FULL
    display = pygame.display.set_mode(
        size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        flags=(FULLSCREEN | SCALED if is_fullscreen else 0) | DOUBLEBUF,
        depth=SURFACE_ARGS['depth']
    )
    clock = Clock()

    while True:
        menu_loop(display, clock)
        game_loop(display, clock)


if __name__ == '__main__':
    main()
