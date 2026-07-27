import pygame
from ecs_pattern import EntityManager, SystemManager
from pygame import Color, Surface
from pygame.time import Clock

from common_tools.consts import FPS_MAX, FPS_SHOW, SCREEN_HEIGHT_PX
from common_tools.resources import FONT_DEFAULT
from demo.entities import DemoData
from demo.systems import SysControl, SysDraw, SysInit


def demo_loop(display: Surface, clock: Clock):
    """Основной цикл demo"""
    entities = EntityManager()
    system_manager = SystemManager([
        SysInit(entities),
        SysControl(entities),
        SysDraw(entities, display),
    ])
    system_manager.start_systems()

    demo_data: DemoData = next(entities.get_by_class(DemoData))

    while demo_data.do_demo:
        clock.tick_busy_loop(FPS_MAX)  # tick_busy_loop точный + ест проц, tick грубый + не ест проц
        system_manager.update_systems()
        if FPS_SHOW:
            display.blit(
                FONT_DEFAULT.render(f'FPS: {int(clock.get_fps())}', True, Color('#1339AC')),
                (0, SCREEN_HEIGHT_PX * 0.98))
        pygame.display.flip()  # draw changes on screen

    system_manager.stop_systems()
