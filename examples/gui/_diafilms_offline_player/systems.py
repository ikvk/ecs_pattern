from sys import exit  # *for windows
from time import monotonic
from typing import Callable, Optional

import pygame
from ecs_pattern import EntityManager, System
from pygame import K_DOWN, K_UP, Surface
from pygame.event import Event
from pygame.locals import K_AC_BACK, K_ESCAPE, KEYDOWN, QUIT
from pygame.math import Vector2

from common_tools.consts import (
    MAIN_SF_HEIGHT_PX,
    MAIN_SF_LEFT_PX,
    MAIN_SF_PADDING_PX,
    MAIN_SF_TOP_PX,
    PLAYER_SCENE_ROOT,
    SCREEN_WIDTH_PX,
    settings_storage,
)
from common_tools.diafilms_data import choose_prev_film, choose_random_film
from common_tools.gui import (
    PA_SWIPE_DOWN,
    PA_SWIPE_UP,
    PointerEventGetter,
    control_button,
    control_scroll,
    draw_button,
    draw_scroll,
    make_attrs_button,
    make_attrs_scroll,
)
from common_tools.resources import (
    IMG_ICON_ARROW_DOWN,
    IMG_ICON_ARROW_UP,
    IMG_ICON_BACK,
    IMG_ICON_FORWARD_DICE,
    IMG_ICON_HOME,
    MUTABLE_RESOURCES,
    SOUND_BUTTON_CLICK,
    SOUND_DENY,
    SOUND_SHIFT,
    SOUND_START,
)
from common_tools.surface import colored_block_surface

from .entities import (
    ButtonFilmNext,
    ButtonFilmPrev,
    ButtonFrameNext,
    ButtonFramePerv,
    ButtonHome,
    FilmFrameCurrent,
    FilmFramePrev,
    PlayerBackground,
    PlayerData,
    ScrollBarFilm,
)
from .surfaces import surface_current_film_frame, surface_player_background


def _load_current_film_data(entities: EntityManager):
    """Загрузить данные текущего фильма в плеер"""
    # данные фильма
    fid = settings_storage.current_film
    frame = settings_storage.current_frame
    frames = MUTABLE_RESOURCES['DIAFILMS_DATA'][fid]['frames']
    frame_count = len(frames)
    frame_index = frames.index(frame) if frame in frames else 0

    # смена кадра
    next(entities.get_by_class(FilmFrameCurrent)).surface = surface_current_film_frame()
    next(entities.get_by_class(FilmFramePrev)).surface = surface_current_film_frame()

    # скролл
    scroll = next(entities.get_by_class(ScrollBarFilm))
    scroll.position_count = frame_count
    scroll.position_current = frame_index
    scroll.position_future = frame_index


def _film_next(entities: EntityManager):
    """Логика открытия следующего диафильма"""
    SOUND_START.play()
    choose_random_film()
    _load_current_film_data(entities)


def _film_prev(entities: EntityManager):
    """Логика открытия предыдущего диафильма"""
    SOUND_BUTTON_CLICK.play()
    choose_prev_film()
    _load_current_film_data(entities)


def _frame_change(entities: EntityManager, scroll_pos_delta: int):
    """Логика смены кадра"""

    # смена позиции кадра
    scroll = next(entities.get_by_class(ScrollBarFilm))
    new_scroll_pos = scroll.position_current + scroll_pos_delta
    if 0 <= new_scroll_pos <= scroll.position_count - 1:
        SOUND_SHIFT.play()
        scroll.position_current = new_scroll_pos
        frames = MUTABLE_RESOURCES['DIAFILMS_DATA'][settings_storage.current_film]['frames']
        settings_storage.current_frame = frames[new_scroll_pos] if 0 <= new_scroll_pos < len(frames) else frames[0]

    # переход к следующему диафильму, если находимся на последнем кадре
    if new_scroll_pos >= scroll.position_count:
        _film_next(entities)
        return

    # предыдущего кадра нет
    if new_scroll_pos < 0:
        SOUND_DENY.play()

    # смена кадра
    film_frame_current = next(entities.get_by_class(FilmFrameCurrent))
    film_frame_prev = next(entities.get_by_class(FilmFramePrev))
    film_frame_prev.surface = film_frame_current.surface
    film_frame_current.surface = surface_current_film_frame()
    film_frame_prev.surface.set_alpha(255)
    film_frame_current.surface.set_alpha(255)

    # инфо для анимации
    next(entities.get_by_class(PlayerData)).last_frame_change_start_time = monotonic()


def on_click_button_frame_next(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    _frame_change(entities, +1)


def on_click_button_frame_perv(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    _frame_change(entities, -1)


def on_change_scrollbar_film(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    _frame_change(entities, 0)


def on_click_button_film_next(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    _film_next(entities)


def on_click_button_film_prev(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    _film_prev(entities)


def on_click_button_home(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    next(entities.get_by_class(PlayerData)).do_play = False


class SysInit(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities

    def start(self):
        _bnt = ButtonHome(scenes=[0], on_click=None, **make_attrs_button(0, 0, colored_block_surface('red', 1, 1)))
        _bnt_w_px = _bnt.rect.width
        _bnt_h_px = _bnt.rect.height
        _bnt_pad_px = _bnt_h_px * 0.33

        _pixel_sf = colored_block_surface('red', 1, 1)

        button_x = SCREEN_WIDTH_PX - _bnt_w_px - MAIN_SF_PADDING_PX
        self.entities.add(
            PlayerData(
                do_play=True,
                scene_active=PLAYER_SCENE_ROOT,
                last_frame_change_start_time=monotonic() - 100,
                last_frame_change_animation_speed_sec=0.62,
                last_frame_was_control_event=False,
            ),
            FilmFrameCurrent(
                x=MAIN_SF_LEFT_PX,
                y=MAIN_SF_TOP_PX,
                surface=_pixel_sf,
            ),
            FilmFramePrev(
                x=MAIN_SF_LEFT_PX,
                y=MAIN_SF_TOP_PX,
                surface=_pixel_sf,
            ),
            PlayerBackground(
                x=0,
                y=0,
                surface=surface_player_background()
            ),
            ScrollBarFilm(
                scenes=[PLAYER_SCENE_ROOT],
                on_change=on_change_scrollbar_film,
                position_count=1,
                position_current=0,
                position_future=0,
                **make_attrs_scroll(
                    x=MAIN_SF_PADDING_PX,
                    y=MAIN_SF_PADDING_PX,
                    height=MAIN_SF_HEIGHT_PX - MAIN_SF_PADDING_PX * 2
                ),
            ),

            # кнопки
            ButtonFramePerv(
                scenes=[PLAYER_SCENE_ROOT],
                on_click=on_click_button_frame_perv,
                **make_attrs_button(
                    x=button_x,
                    y=MAIN_SF_HEIGHT_PX / 2 - _bnt_pad_px - _bnt_h_px,
                    icon=IMG_ICON_ARROW_UP
                ),
            ),
            ButtonFrameNext(
                scenes=[PLAYER_SCENE_ROOT],
                on_click=on_click_button_frame_next,
                **make_attrs_button(
                    x=button_x,
                    y=MAIN_SF_HEIGHT_PX / 2,
                    icon=IMG_ICON_ARROW_DOWN
                ),
            ),

            ButtonFilmPrev(
                scenes=[PLAYER_SCENE_ROOT],
                on_click=on_click_button_film_prev,
                **make_attrs_button(
                    x=button_x,
                    y=MAIN_SF_HEIGHT_PX - MAIN_SF_PADDING_PX - _bnt_h_px * 1 - _bnt_pad_px * 1,
                    icon=IMG_ICON_BACK
                ),
            ),
            ButtonFilmNext(
                scenes=[PLAYER_SCENE_ROOT],
                on_click=on_click_button_film_next,
                **make_attrs_button(
                    x=button_x,
                    y=MAIN_SF_HEIGHT_PX - MAIN_SF_PADDING_PX - _bnt_h_px * 2 - _bnt_pad_px * 2,
                    icon=IMG_ICON_FORWARD_DICE
                ),
            ),

            ButtonHome(
                scenes=[PLAYER_SCENE_ROOT],
                on_click=on_click_button_home,
                **make_attrs_button(button_x, MAIN_SF_PADDING_PX, IMG_ICON_HOME),
            ),
        )

        _load_current_film_data(self.entities)
        _frame_change(self.entities, 0)


class SysControl(System):
    def __init__(self, entities: EntityManager):  # noqa
        self.entities = entities
        self.event_getter: Callable[..., list[Event]] = pygame.event.get
        self.pd = None
        self.pointer_event_getter = None
        self._last_frame_was_control_event = False

    def start(self):
        self.pd = next(self.entities.get_by_class(PlayerData))
        self.pointer_event_getter = PointerEventGetter()

    def update(self):
        self._last_frame_was_control_event = False

        for event in self.event_getter():
            self._last_frame_was_control_event = True
            event_type = event.type
            event_key = getattr(event, 'key', None)

            # закрыть окно
            if event_type == QUIT:
                exit()

            # ескейп или назад на андроид
            if event_type == KEYDOWN and event_key in (K_ESCAPE, K_AC_BACK):
                self.pd.do_play = False

            # управление кадрами - кнопки и события указателя (мыши или пальца)
            pointer_action = self.pointer_event_getter.get_pointer_action(event)
            if pointer_action == PA_SWIPE_UP or event_type == KEYDOWN and event_key == K_DOWN:
                _frame_change(self.entities, +1)
            if pointer_action == PA_SWIPE_DOWN or event_type == KEYDOWN and event_key == K_UP:
                _frame_change(self.entities, -1)

            # gui
            if control_button(event, event_type, self.pd.scene_active, self.entities):
                continue
            if control_scroll(event, event_type, self.pd.scene_active, self.entities):
                continue

        # флаг для оптимизации
        self.pd.last_frame_was_control_event = self._last_frame_was_control_event


class SysDraw(System):
    def __init__(self, entities: EntityManager, display: Surface):
        self.entities = entities
        self.display = display
        self.pd: Optional[PlayerData] = None
        self.background = None
        self.film_frame_current = None
        self.film_frame_prev = None
        self.scroll = None

    def start(self):
        self.pd = next(self.entities.get_by_class(PlayerData))
        self.background = next(self.entities.get_by_class(PlayerBackground))
        self.film_frame_current = next(self.entities.get_by_class(FilmFrameCurrent))
        self.film_frame_prev = next(self.entities.get_by_class(FilmFramePrev))
        self.scroll = next(self.entities.get_by_class(ScrollBarFilm))

    def update(self):
        now_time = monotonic()

        # времени прошло после начала последнего перелистывания
        last_frame_change_start_time_delta = now_time - self.pd.last_frame_change_start_time

        # листали давно, анимации нет и не было событий - рисуем кадры редко, экономим батарею
        if last_frame_change_start_time_delta > self.pd.last_frame_change_animation_speed_sec and now_time % 1 > 0.035 \
                and not self.pd.last_frame_was_control_event:
            return

        # фон
        self.display.blit(self.background.surface, (self.background.x, self.background.y))

        # текущий кадр
        self.display.blit(self.film_frame_current.surface, (self.film_frame_current.x, self.film_frame_current.y))

        # плавная смена кадра
        if last_frame_change_start_time_delta <= self.pd.last_frame_change_animation_speed_sec:
            a1 = min(last_frame_change_start_time_delta / self.pd.last_frame_change_animation_speed_sec * 255, 255)
            a2 = 255 - a1
            if a2 > 8:
                # иначе виден рывок
                self.film_frame_prev.surface.set_alpha(a2)
                self.display.blit(self.film_frame_prev.surface, (self.film_frame_prev.x, self.film_frame_prev.y))

        # gui
        draw_button(self.display, self.pd.scene_active, self.entities)
        draw_scroll(self.display, self.pd.scene_active, self.entities)
