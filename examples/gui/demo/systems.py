from sys import exit  # *for windows
from typing import Callable, Optional

import pygame
from ecs_pattern import EntityManager, System
from pygame import Surface
from pygame.event import Event
from pygame.locals import K_AC_BACK, K_ESCAPE, KEYDOWN, QUIT
from pygame.math import Vector2

from common_tools.consts import SCREEN_HEIGHT_PX, SCREEN_WIDTH_PX
from common_tools.gui import (
    control_button,
    control_checkbox,
    control_input_activate,
    control_input_edit,
    control_scroll,
    draw_button,
    draw_checkbox,
    draw_input,
    draw_scroll,
    draw_text,
    make_attrs_button,
    make_attrs_checkbox,
    make_attrs_input,
    make_attrs_scroll,
    make_attrs_text,
)
from common_tools.resources import FONT_UI_TEXT, IMG_ICON_DICE
from common_tools.surface import colored_block_surface, text_surface

from .entities import Button1, Checkbox1, DemoData, Input1, ScrollBar1, Text1


def on_click_button1(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    print('on_click_button1')


def on_click_button2(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    print('on_click_button2')


def on_change_checkbox1(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    print('on_change_checkbox1', next(entities.get_by_class(Checkbox1)).checked)


def on_change_scrollbar1(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    scroll = next(entities.get_by_class(ScrollBar1))
    print(f'on_change_scrollbar1 {scroll.position_current + 1} из {scroll.position_count}')


def on_confirm_input1(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    print('on_confirm_input1', next(entities.get_by_class(Input1)).text)


def on_change_input1(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    print('on_change_input1 ...', next(entities.get_by_class(Input1)).text)


DEMO_SCENE_ROOT = 1


class SysInit(System):

    def __init__(self, entities: EntityManager):
        self.entities = entities

    def start(self):
        self.entities.add(
            DemoData(do_demo=True, scene_active=DEMO_SCENE_ROOT),
            Button1(
                scenes=[DEMO_SCENE_ROOT],
                on_click=on_click_button1,
                **make_attrs_button(50, 50, IMG_ICON_DICE, text='Button1'),
            ),
            Button1(
                scenes=[DEMO_SCENE_ROOT],
                on_click=on_click_button2,
                **make_attrs_button(50, 250, IMG_ICON_DICE),
            ),
            Checkbox1(
                scenes=[DEMO_SCENE_ROOT],
                on_change=on_change_checkbox1,
                checked=True,
                **make_attrs_checkbox(50, 450, 'Checkbox1'),
            ),
            ScrollBar1(
                scenes=[DEMO_SCENE_ROOT],
                on_change=on_change_scrollbar1,
                position_count=25,
                position_current=0,
                position_future=0,
                **make_attrs_scroll(550, 50, height=700),
            ),
            Input1(
                scenes=[DEMO_SCENE_ROOT],
                on_confirm=on_confirm_input1,
                on_change=on_change_input1,
                max_length=20,
                text='Привет!',
                **make_attrs_input(50, 650, 'search text'),
            ),
            Text1(
                scenes=[DEMO_SCENE_ROOT],
                **make_attrs_text(
                    50, 850, text_surface(FONT_UI_TEXT, 'Text1', '#E32636', '#EEEEEE', 0.05)),
            ),
        )


class SysControl(System):

    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.event_getter: Callable[..., list[Event]] = pygame.event.get
        self.dd = None

    def start(self):
        self.dd = next(self.entities.get_by_class(DemoData))

    def update(self):
        for event in self.event_getter():
            event_type = event.type
            event_key = getattr(event, 'key', None)

            # закрыть
            if event_type == QUIT:
                exit()
            if event_type == KEYDOWN and event_key in (K_ESCAPE, K_AC_BACK):
                exit()

            # gui
            if control_button(event, event_type, self.dd.scene_active, self.entities):
                continue
            if control_checkbox(event, event_type, self.dd.scene_active, self.entities):
                continue
            if control_scroll(event, event_type, self.dd.scene_active, self.entities):
                continue
            control_input_activate(event, event_type, self.dd.scene_active, self.entities)
            control_input_edit(event, event_type, event_key, self.dd.scene_active, self.entities)


class SysDraw(System):

    def __init__(self, entities: EntityManager, display: Surface):
        self.entities = entities
        self.display = display
        self.dd: Optional[DemoData] = None
        self.background_sf = None

    def start(self):
        self.dd = next(self.entities.get_by_class(DemoData))
        self.background_sf = colored_block_surface('#888888', SCREEN_WIDTH_PX, SCREEN_HEIGHT_PX)

    def update(self):
        # фон
        self.display.blit(self.background_sf, (0, 0))

        # gui
        draw_button(self.display, self.dd.scene_active, self.entities)
        draw_input(self.display, self.dd.scene_active, self.entities)
        draw_checkbox(self.display, self.dd.scene_active, self.entities)
        draw_text(self.display, self.dd.scene_active, self.entities)
        draw_scroll(self.display, self.dd.scene_active, self.entities)
