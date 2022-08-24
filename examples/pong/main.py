import os

import pygame
from ecs_pattern import EntityManager, SystemManager

from consts import FPS_MAX
from entities import GameStateInfo
from systems import SysControl, SysDraw, SysGoal, SysMovement, SysInit, SysRoundStarter

os.environ['SDL_VIDEO_CENTERED'] = '1'  # window at center


def pong():
    """Pong game"""

    pygame.init()  # init all imported pygame modules
    pygame.display.set_caption('Pong')
    screen = pygame.display.set_mode((800, 500))  # w h
    clock = pygame.time.Clock()

    entities = EntityManager()

    system_manager = SystemManager([
        SysInit(entities),
        SysControl(entities, pygame.event.get),
        SysMovement(entities),
        SysRoundStarter(entities, clock),
        SysGoal(entities),
        SysDraw(entities, screen),
    ])

    system_manager.start_systems()

    game_state_info: GameStateInfo = next(entities.get_by_class(GameStateInfo))
    while game_state_info.play:
        clock.tick(FPS_MAX)  # tick_busy_loop точный + ест проц, tick грубый + не ест проц
        system_manager.update_systems()
        pygame.display.flip()  # draw changes on screen

    system_manager.stop_systems()


if __name__ == '__main__':
    pong()
