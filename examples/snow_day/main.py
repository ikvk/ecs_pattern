import os

import pygame
from pygame import FULLSCREEN, DOUBLEBUF, SCALED
from pygame.time import Clock

from common_tools.consts import SCREEN_WIDTH, SCREEN_HEIGHT, SURFACE_ARGS, SETTING_SCREEN_IS_FULLSCREEN
from scene1.main import scene1_loop

os.environ['SDL_VIDEO_CENTERED'] = '1'  # window at center


def main():
    """Точка входа в приложение"""
    pygame.display.set_caption('Snow day')
    display = pygame.display.set_mode(
        size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        flags=(FULLSCREEN | SCALED if SETTING_SCREEN_IS_FULLSCREEN else 0) | DOUBLEBUF,
        depth=SURFACE_ARGS['depth']
    )
    clock = Clock()

    while True:
        scene1_loop(display, clock)


if __name__ == '__main__':
    main()
