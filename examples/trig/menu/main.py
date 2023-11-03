import pygame
from pygame import Color, Surface
from pygame.time import Clock
from ecs_pattern import EntityManager, SystemManager

from common_tools.resources import FONT_DEFAULT
from common_tools.consts import FPS_MAX, SCREEN_HEIGHT, FPS_SHOW
from menu.entities import MenuData
from menu.systems import SysControl, SysDraw, SysInit, SysLive


def menu_loop(display: Surface, clock: Clock):
    """Основной цикл меню игры"""
    try:
        import pyi_splash  # noqa (PyInstaller splash screen, поставляется вместе с ним)
        pyi_splash.close()
    except Exception:  # noqa
        pass

    entities = EntityManager()
    system_manager = SystemManager([
        SysInit(entities),
        SysControl(entities),
        SysLive(entities, clock),
        SysDraw(entities, display),
    ])
    system_manager.start_systems()

    menu_data: MenuData = next(entities.get_by_class(MenuData))

    while menu_data.do_menu:
        clock.tick_busy_loop(FPS_MAX)  # tick_busy_loop точный + ест проц, tick грубый + не ест проц
        system_manager.update_systems()
        if FPS_SHOW:
            display.blit(
                FONT_DEFAULT.render(f'FPS: {int(clock.get_fps())}', True, Color('#1339AC')), (0, SCREEN_HEIGHT * 0.98))
        pygame.display.flip()  # draw changes on screen

    system_manager.stop_systems()
