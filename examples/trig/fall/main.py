import pygame
from ecs_pattern import EntityManager, SystemManager
from pygame import Color, Surface
from pygame.time import Clock

from common_tools.consts import FPS_MAX, FPS_SHOW, SCREEN_HEIGHT_PX
from common_tools.resources import FONT_DEFAULT
from fall.entities import GameData
from fall.systems import SysControl, SysDraw, SysInit, SysLive, SysLiveFigure


def game_loop(display: Surface, clock: Clock):
    """Основной цикл игры"""
    entities = EntityManager()
    system_manager = SystemManager([
        SysInit(entities),
        SysControl(entities),
        SysLiveFigure(entities),
        SysLive(entities, clock),
        SysDraw(entities, display),
    ])
    system_manager.start_systems()

    game_data: GameData = next(entities.get_by_class(GameData))

    while game_data.do_play:
        clock.tick_busy_loop(FPS_MAX)  # tick_busy_loop точный + ест проц, tick грубый + не ест проц
        system_manager.update_systems()
        if FPS_SHOW:
            display.blit(
                FONT_DEFAULT.render(f'FPS: {int(clock.get_fps())}', True, Color('#1339AC')),
                (0, SCREEN_HEIGHT_PX * 0.98)
            )
        pygame.display.flip()  # draw changes on screen

    system_manager.stop_systems()
