from random import randint
from sys import exit  # *for windows
from time import monotonic, sleep
from typing import Callable, Optional

import pygame
from ecs_pattern import EntityManager, System
from pygame import BLEND_RGBA_MULT, Rect, Surface
from pygame.event import Event
from pygame.locals import K_AC_BACK, K_ESCAPE, KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, QUIT
from pygame.math import Vector2
from pygame.transform import smoothscale

from common_tools.components import ComAnimated, ComSpeed
from common_tools.consts import (
    BS_STATIC,
    BUTTON_WIDTH,
    FPS_MAX,
    GRID_HEIGHT,
    MENU_ROOT_AREA_BUTTONS_HEIGHT,
    MENU_ROOT_AREA_GAME_NAME_HEIGHT,
    MENU_ROOT_BUTTON_GROUP_GAP_WIDTH,
    MENU_ROOT_BUTTON_GROUP_WIDTH,
    MENU_SCENE_ABOUT,
    MENU_SCENE_GUIDE,
    MENU_SCENE_RECORDS,
    MENU_SCENE_ROOT,
    MENU_SCENE_SETTINGS,
    MENU_SHINE_WIDTH,
    SCREEN_HEIGHT_PX,
    SCREEN_WIDTH_PX,
    SETTINGS_STORAGE,
    SURFACE_ARGS,
    TEXT_ML_HEIGHT,
    TEXT_ML_WIDTH,
)
from common_tools.gui import control_button, draw_button, draw_text_ml, gui_button_attrs
from common_tools.i18n import (
    I18N_BUTTON_TO_MENU_ROOT,
    I18N_SETTING_GRAPHIC_HIGH,
    I18N_SETTING_GRAPHIC_LOW,
    I18N_SETTING_GRAPHIC_MIDDLE,
    I18N_SETTING_LANGUAGE_EN,
    I18N_SETTING_LANGUAGE_RU,
    I18N_SETTING_SCREEN_MODE_FULL,
    I18N_SETTING_SCREEN_MODE_WINDOW,
    I18N_SETTING_SOUND_DISABLED,
    I18N_SETTING_SOUND_NORMAL,
    I18N_SETTING_SOUND_QUIET,
)
from common_tools.math import normal_distribution
from common_tools.resources import (
    FONT_TEXT_ML,
    IMG_BUTTON_ROOT_1,
    IMG_BUTTON_ROOT_2,
    IMG_BUTTON_ROOT_3,
    IMG_BUTTON_ROOT_4,
    IMG_BUTTON_ROOT_5,
    IMG_BUTTON_ROOT_6,
    IMG_DUST,
    IMG_ICON_ABOUT,
    IMG_ICON_EXIT,
    IMG_ICON_GUIDE,
    IMG_ICON_PLAY,
    IMG_ICON_RECORDS,
    IMG_ICON_SETTINGS,
    IMG_TRI_GRID,
    SOUND_BUTTON_CLICK,
    SOUND_DENY,
    SOUND_MENU,
    SOUND_START,
    set_sound_volume,
)
from common_tools.settings import (
    SETTING_GRAPHIC_HIGH,
    SETTING_GRAPHIC_LOW,
    SETTING_GRAPHIC_MIDDLE,
    SETTING_LANGUAGE_EN,
    SETTING_LANGUAGE_RU,
    SETTING_SCREEN_MODE_FULL,
    SETTING_SCREEN_MODE_WINDOW,
    SETTING_SOUND_DISABLED,
    SETTING_SOUND_NORMAL,
    SETTING_SOUND_QUIET,
)
from common_tools.surface import colored_block_surface, colorize_surface, shine_surface, texture_onto_sf

from .entities import (
    Background,
    ButtonAbout,
    ButtonExit,
    ButtonGraphicHigh,
    ButtonGraphicLow,
    ButtonGraphicMiddle,
    ButtonGuide,
    ButtonLanguageEn,
    ButtonLanguageRu,
    ButtonPlay,
    ButtonRecords,
    ButtonScreenModeFull,
    ButtonScreenModeWindow,
    ButtonSettings,
    ButtonSoundDisable,
    ButtonSoundNormal,
    ButtonSoundQuiet,
    ButtonToMenuRoot,
    Dust,
    DustAnimationSet,
    LabelGameName,
    MenuData,
    Shine,
    ShineLightAnimationSet,
    TextAbout,
    TextGuide,
    TextRecords,
    TextSettings,
)
from .surfaces import (
    surface_background,
    surface_dust,
    surface_label_game_name,
    surface_shine_animation_set,
    surface_text_about,
    surface_text_guide,
    surface_text_records,
    surface_text_settings,
)


def _dust_spawn(entities: EntityManager):
    """Создать пылинку на произвольной позиции"""
    speed_max = int(SCREEN_HEIGHT_PX * GRID_HEIGHT / 26)
    entities.add(
        Dust(
            animation_set=next(entities.get_by_class(DustAnimationSet)),
            animation_looped=False,
            animation_frame=255,
            animation_frame_float=255.0,
            animation_speed=randint(10, 50),
            x=randint(0, SCREEN_WIDTH_PX),
            y=randint(0, SCREEN_HEIGHT_PX),
            speed_x=randint(-speed_max, speed_max),
            speed_y=randint(-speed_max, speed_max),
        )
    )


def on_click_to_menu_root(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    next(entities.get_by_class(MenuData)).scene_active = MENU_SCENE_ROOT


def on_click_about(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    next(entities.get_by_class(MenuData)).scene_active = MENU_SCENE_ABOUT


def on_click_exit(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    sleep(SOUND_BUTTON_CLICK.get_length())
    exit()


def on_click_guide(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    next(entities.get_by_class(MenuData)).scene_active = MENU_SCENE_GUIDE


def on_click_play(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_START.play()
    next(entities.get_by_class(MenuData)).do_menu = False


def on_click_records(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    next(entities.get_by_class(MenuData)).scene_active = MENU_SCENE_RECORDS


def on_click_settings(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    next(entities.get_by_class(MenuData)).scene_active = MENU_SCENE_SETTINGS


def on_click_graphic_high(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    SETTINGS_STORAGE.graphic = SETTING_GRAPHIC_HIGH
    next(entities.get_by_class(TextSettings)).sf_text = surface_text_settings()


def on_click_graphic_low(entities: EntityManager, pointer_pos: Vector2):  # noqa
    if SETTINGS_STORAGE.screen_mode == SETTING_SCREEN_MODE_FULL:
        SOUND_BUTTON_CLICK.play()
        SETTINGS_STORAGE.graphic = SETTING_GRAPHIC_LOW
        next(entities.get_by_class(TextSettings)).sf_text = surface_text_settings()
    else:
        SOUND_DENY.play()


def on_click_graphic_middle(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    SETTINGS_STORAGE.graphic = SETTING_GRAPHIC_MIDDLE
    next(entities.get_by_class(TextSettings)).sf_text = surface_text_settings()


def on_click_screen_mode_full(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    SETTINGS_STORAGE.screen_mode = SETTING_SCREEN_MODE_FULL
    next(entities.get_by_class(TextSettings)).sf_text = surface_text_settings()


def on_click_screen_mode_window(entities: EntityManager, pointer_pos: Vector2):  # noqa
    if SETTINGS_STORAGE.is_android:
        SOUND_DENY.play()
    else:
        SOUND_BUTTON_CLICK.play()
        SETTINGS_STORAGE.screen_mode = SETTING_SCREEN_MODE_WINDOW
        next(entities.get_by_class(TextSettings)).sf_text = surface_text_settings()


def on_click_sound_disable(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SETTINGS_STORAGE.sound = SETTING_SOUND_DISABLED
    next(entities.get_by_class(TextSettings)).sf_text = surface_text_settings()
    set_sound_volume(SETTING_SOUND_DISABLED)
    SOUND_BUTTON_CLICK.play()


def on_click_sound_normal(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SETTINGS_STORAGE.sound = SETTING_SOUND_NORMAL
    next(entities.get_by_class(TextSettings)).sf_text = surface_text_settings()
    set_sound_volume(SETTING_SOUND_NORMAL)
    SOUND_BUTTON_CLICK.play()


def on_click_sound_quiet(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SETTINGS_STORAGE.sound = SETTING_SOUND_QUIET
    next(entities.get_by_class(TextSettings)).sf_text = surface_text_settings()
    set_sound_volume(SETTING_SOUND_QUIET)
    SOUND_BUTTON_CLICK.play()


def on_click_language_ru(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    SETTINGS_STORAGE.language = SETTING_LANGUAGE_RU
    next(entities.get_by_class(TextSettings)).sf_text = surface_text_settings()


def on_click_language_en(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    SETTINGS_STORAGE.language = SETTING_LANGUAGE_EN
    next(entities.get_by_class(TextSettings)).sf_text = surface_text_settings()


def _gui_button_root(icon: Surface, bg: Surface, root_num: int) -> dict:
    upward = root_num in (1, 3, 5)
    tri_gap_width = SCREEN_WIDTH_PX * MENU_ROOT_BUTTON_GROUP_GAP_WIDTH
    tri_width = SCREEN_WIDTH_PX * MENU_ROOT_BUTTON_GROUP_WIDTH / 2 - tri_gap_width * 2
    scale_rate = tri_width / bg.get_width()
    icon_size_rate = 0.41  # размер относительно треугольника

    bg = smoothscale(bg.convert_alpha(), (tri_width, bg.get_height() * scale_rate))
    icon = smoothscale(icon.convert_alpha(), (tri_width * icon_size_rate, tri_width * icon_size_rate))  # квадратная
    icon.set_alpha(250)

    icon_shine_size = int(icon.get_width() * 0.05)
    icon_shine_sf_alpha = 30
    icon_shine_color = '#333333'
    icon_sf_hover = shine_surface(
        colorize_surface(icon, '#7FFFD4'), icon_shine_color, icon_shine_size, icon_shine_sf_alpha)  # Aquamarine
    icon_sf_hover = texture_onto_sf(IMG_TRI_GRID, icon_sf_hover, BLEND_RGBA_MULT)
    icon_sf_static = shine_surface(
        colorize_surface(icon, '#FFD700'), icon_shine_color, icon_shine_size, icon_shine_sf_alpha)
    icon_sf_static = texture_onto_sf(IMG_TRI_GRID, icon_sf_static, BLEND_RGBA_MULT)
    icon_sf_w, icon_sf_h = icon_sf_static.get_size()

    bg_shine_size = int(bg.get_width() * 0.05)
    bg_shine_size_alt = int(bg.get_width() * 0.02)
    bg_shine_size2 = int(bg.get_width() * 0.005)
    if SETTINGS_STORAGE.is_android:
        bg_sf_shine_static = shine_surface(bg, "#8B4513", bg_shine_size, 3, bg_shine_size_alt)
        bg_sf_shine_static2 = shine_surface(bg, "#111111", bg_shine_size2, 1)
        bg_sf_shine_hover = shine_surface(bg, "#FF4500", bg_shine_size, 10, bg_shine_size_alt)
    else:
        bg_sf_shine_static = shine_surface(bg, "#8B4513", bg_shine_size, 3)  # slow
        bg_sf_shine_static2 = shine_surface(bg, "#111111", bg_shine_size2, 1)
        bg_sf_shine_hover = shine_surface(bg, "#FF4500", bg_shine_size, 6)  # slow

    w, h = bg_sf_shine_hover.get_size()
    icon_h_fix = (1 if upward else -1) * icon_sf_h * 0.3
    icon_center_point = (w / 2 - icon_sf_w / 2, (h / 2 - icon_sf_h / 2) + icon_h_fix)

    sf_static = Surface((w, h), **SURFACE_ARGS)
    sf_static.blit(bg_sf_shine_static, (0, 0))
    sf_static.blit(bg_sf_shine_static2, (bg_shine_size - bg_shine_size2, bg_shine_size - bg_shine_size2))
    sf_static.blit(icon_sf_static, icon_center_point)

    sf_hover = Surface((w, h), **SURFACE_ARGS)
    sf_hover.blit(bg_sf_shine_hover, (0, 0))
    sf_hover.blit(icon_sf_static, icon_center_point)

    sf_pressed = Surface((w, h), **SURFACE_ARGS)
    sf_pressed.blit(bg_sf_shine_hover, (0, 0))
    sf_pressed.blit(icon_sf_hover, icon_center_point)

    _w_center = SCREEN_WIDTH_PX / 2
    _h_center = SCREEN_HEIGHT_PX - SCREEN_HEIGHT_PX * MENU_ROOT_AREA_BUTTONS_HEIGHT / 2
    _gap = SCREEN_WIDTH_PX * MENU_ROOT_BUTTON_GROUP_GAP_WIDTH
    # против часовой от правого верхнего треугольника
    if root_num == 1:
        x = _w_center + _gap
        y = _h_center - h - _gap / 2
    elif root_num == 2:
        x = _w_center - w / 2
        y = _h_center - h - _gap / 2
    elif root_num == 3:
        x = _w_center - w - _gap
        y = _h_center - h - _gap / 2
    elif root_num == 4:
        x = _w_center - w - _gap
        y = _h_center + _gap / 2
    elif root_num == 5:
        x = _w_center - w / 2
        y = _h_center + _gap / 2
    elif root_num == 6:
        x = _w_center + _gap
        y = _h_center + _gap / 2
    else:
        raise ValueError('wrong root_num')

    x_corr = 0
    y_corr = (1 if upward else -1) * SCREEN_WIDTH_PX * MENU_ROOT_BUTTON_GROUP_GAP_WIDTH * 0.7  # равномерный gap
    return dict(
        rect=Rect(x + x_corr, y + y_corr, w, h),
        sf_static=sf_static,
        sf_hover=sf_hover,
        sf_pressed=sf_pressed,
        mask=pygame.mask.from_surface(sf_static),
        state=BS_STATIC,
    )


class SysInit(System):

    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.music_channel = None

    def start(self):
        set_sound_volume(SETTINGS_STORAGE.sound)

        _surface_text_about = surface_text_about()
        _surface_text_records = surface_text_records()
        _surface_text_guide = surface_text_guide()
        _surface_text_settings = surface_text_settings()
        _surface_label_game_name = surface_label_game_name()

        _tw = SCREEN_WIDTH_PX * TEXT_ML_WIDTH
        _th = SCREEN_HEIGHT_PX * TEXT_ML_HEIGHT
        _xpad = (SCREEN_WIDTH_PX - _tw) / 2
        common_text_ml_rect = (  # (left, top, width, height)
            _xpad,
            _xpad,
            _tw,
            _th,
        )

        self.entities.init(
            Dust([], False, 0, 0, 0, 0, 0, 0, 0),
        )

        _height_center_px_game_name = SCREEN_HEIGHT_PX * MENU_ROOT_AREA_GAME_NAME_HEIGHT / 2
        _height_center_px_main_buttons = SCREEN_HEIGHT_PX - SCREEN_HEIGHT_PX * MENU_ROOT_AREA_BUTTONS_HEIGHT / 2

        _btn_x_gap = SCREEN_WIDTH_PX * 0.02
        _btn_w = SCREEN_WIDTH_PX * BUTTON_WIDTH
        _btn_pad = SCREEN_WIDTH_PX * 0.04

        _text_linesize = FONT_TEXT_ML.get_linesize()
        _text_y_pad = (SCREEN_HEIGHT_PX - SCREEN_HEIGHT_PX * TEXT_ML_HEIGHT) / 2 - FONT_TEXT_ML.get_linesize() * 0.2

        normal_dist_data = normal_distribution(list(range(256)), 128, 10)
        normal_dist_max_val = max(normal_dist_data)
        dust_alpha_dist = [int(i * 255 / normal_dist_max_val) for i in normal_dist_data]

        self.entities.add(
            MenuData(
                do_menu=True,
                scene_active=MENU_SCENE_ROOT,
                music_channel=SOUND_MENU.play(-1),
                last_dust_spawn_time=0,
            ),
            Background(
                surface_background(),
                x=0,
                y=0,
            ),
            LabelGameName(
                _surface_label_game_name,
                x=SCREEN_WIDTH_PX / 2 - _surface_label_game_name.get_width() / 2,
                y=_height_center_px_game_name - _surface_label_game_name.get_height() / 2,
            ),
            ButtonToMenuRoot(
                scenes=[MENU_SCENE_ABOUT, MENU_SCENE_GUIDE, MENU_SCENE_RECORDS, MENU_SCENE_SETTINGS],
                on_click=on_click_to_menu_root,
                **gui_button_attrs(
                    SCREEN_WIDTH_PX * 0.25, SCREEN_HEIGHT_PX * 0.85,
                    I18N_BUTTON_TO_MENU_ROOT, 1.61),
            ),

            DustAnimationSet(
                tuple(surface_dust(IMG_DUST, i) for i in dust_alpha_dist)
            ),

            # root
            ButtonAbout(
                scenes=[MENU_SCENE_ROOT],
                on_click=on_click_about,
                **_gui_button_root(IMG_ICON_ABOUT, IMG_BUTTON_ROOT_3, 3),
            ),
            ButtonExit(
                scenes=[MENU_SCENE_ROOT],
                on_click=on_click_exit,
                **_gui_button_root(IMG_ICON_EXIT, IMG_BUTTON_ROOT_4, 4),
            ),
            ButtonGuide(
                scenes=[MENU_SCENE_ROOT],
                on_click=on_click_guide,
                **_gui_button_root(IMG_ICON_GUIDE, IMG_BUTTON_ROOT_1, 1),
            ),
            ButtonPlay(
                scenes=[MENU_SCENE_ROOT],
                on_click=on_click_play,
                **_gui_button_root(IMG_ICON_PLAY, IMG_BUTTON_ROOT_5, 5),
            ),
            ButtonRecords(
                scenes=[MENU_SCENE_ROOT],
                on_click=on_click_records,
                **_gui_button_root(IMG_ICON_RECORDS, IMG_BUTTON_ROOT_2, 2),
            ),
            ButtonSettings(
                scenes=[MENU_SCENE_ROOT],
                on_click=on_click_settings,
                **_gui_button_root(IMG_ICON_SETTINGS, IMG_BUTTON_ROOT_6, 6),
            ),

            # graphic
            ButtonGraphicLow(
                scenes=[MENU_SCENE_SETTINGS],
                on_click=on_click_graphic_low,
                **gui_button_attrs(
                    _btn_pad + _btn_x_gap, _text_y_pad + _text_linesize * 3,
                    I18N_SETTING_GRAPHIC_LOW),
            ),
            ButtonGraphicMiddle(
                scenes=[MENU_SCENE_SETTINGS],
                on_click=on_click_graphic_middle,
                **gui_button_attrs(
                    _btn_pad + _btn_x_gap * 2 + _btn_w, _text_y_pad + _text_linesize * 3,
                    I18N_SETTING_GRAPHIC_MIDDLE),
            ),
            ButtonGraphicHigh(
                scenes=[MENU_SCENE_SETTINGS],
                on_click=on_click_graphic_high,
                **gui_button_attrs(
                    _btn_pad + _btn_x_gap * 3 + _btn_w * 2, _text_y_pad + _text_linesize * 3,
                    I18N_SETTING_GRAPHIC_HIGH),
            ),

            # screen mode
            ButtonScreenModeFull(
                scenes=[MENU_SCENE_SETTINGS],
                on_click=on_click_screen_mode_full,
                **gui_button_attrs(
                    _btn_pad + _btn_x_gap, _text_y_pad + _text_linesize * 8,
                    I18N_SETTING_SCREEN_MODE_FULL),
            ),
            ButtonScreenModeWindow(
                scenes=[MENU_SCENE_SETTINGS],
                on_click=on_click_screen_mode_window,
                **gui_button_attrs(
                    _btn_pad + _btn_x_gap * 2 + _btn_w, _text_y_pad + _text_linesize * 8,
                    I18N_SETTING_SCREEN_MODE_WINDOW),
            ),

            # sound
            ButtonSoundDisable(
                scenes=[MENU_SCENE_SETTINGS],
                on_click=on_click_sound_disable,
                **gui_button_attrs(
                    _btn_pad + _btn_x_gap, _text_y_pad + _text_linesize * 13,
                    I18N_SETTING_SOUND_DISABLED),
            ),
            ButtonSoundQuiet(
                scenes=[MENU_SCENE_SETTINGS],
                on_click=on_click_sound_quiet,
                **gui_button_attrs(
                    _btn_pad + _btn_x_gap * 2 + _btn_w, _text_y_pad + _text_linesize * 13,
                    I18N_SETTING_SOUND_QUIET),
            ),
            ButtonSoundNormal(
                scenes=[MENU_SCENE_SETTINGS],
                on_click=on_click_sound_normal,
                **gui_button_attrs(
                    _btn_pad + _btn_x_gap * 3 + _btn_w * 2, _text_y_pad + _text_linesize * 13,
                    I18N_SETTING_SOUND_NORMAL),
            ),

            # language
            ButtonLanguageRu(
                scenes=[MENU_SCENE_SETTINGS],
                on_click=on_click_language_ru,
                **gui_button_attrs(
                    _btn_pad + _btn_x_gap, _text_y_pad + _text_linesize * 18,
                    I18N_SETTING_LANGUAGE_RU),
            ),
            ButtonLanguageEn(
                scenes=[MENU_SCENE_SETTINGS],
                on_click=on_click_language_en,
                **gui_button_attrs(
                    _btn_pad + _btn_x_gap * 2 + _btn_w, _text_y_pad + _text_linesize * 18,
                    I18N_SETTING_LANGUAGE_EN),
            ),

            # shine
            Shine(
                x=SCREEN_WIDTH_PX / 2 - SCREEN_WIDTH_PX * MENU_SHINE_WIDTH / 2,
                y=_height_center_px_main_buttons - SCREEN_WIDTH_PX * MENU_SHINE_WIDTH / 2,
                animation_set=ShineLightAnimationSet(surface_shine_animation_set('#FFFF00')),
                animation_looped=True,
                animation_frame=0,
                animation_frame_float=0.0,
                animation_speed=10,
            ),

            # texts
            TextAbout(
                scenes=[MENU_SCENE_ABOUT],
                rect=common_text_ml_rect,
                sf_text=_surface_text_about,
                sf_bg=colored_block_surface('#FFE4B599', *_surface_text_about.get_size()),
            ),
            TextRecords(
                scenes=[MENU_SCENE_RECORDS],
                rect=common_text_ml_rect,
                sf_text=_surface_text_records,
                sf_bg=colored_block_surface('#FFE4B599', *_surface_text_records.get_size()),
            ),
            TextGuide(
                scenes=[MENU_SCENE_GUIDE],
                rect=common_text_ml_rect,
                sf_text=_surface_text_guide,
                sf_bg=colored_block_surface('#FFE4B599', *_surface_text_guide.get_size()),
            ),
            TextSettings(
                scenes=[MENU_SCENE_SETTINGS],
                rect=common_text_ml_rect,
                sf_text=_surface_text_settings,
                sf_bg=colored_block_surface('#FFE4B599', *_surface_text_settings.get_size()),
            ),
        )

    def stop(self):
        next(self.entities.get_by_class(MenuData)).music_channel.stop()


class SysLive(System):

    def __init__(self, entities: EntityManager, clock: pygame.time.Clock):
        self.entities = entities
        self.clock = clock
        self.md = None

    def start(self):
        self.md = next(self.entities.get_by_class(MenuData))

    def update(self):
        now_fps = self.clock.get_fps() or FPS_MAX
        now_time = monotonic()

        # пылинки
        if now_time - self.md.last_dust_spawn_time > 0.5:  # скорость 1 раз в 0.5сек - около 15 одновременных пылинок
            self.md.last_dust_spawn_time = now_time
            _dust_spawn(self.entities)

        # движение
        for speed_obj in self.entities.get_with_component(ComSpeed):
            speed_obj.x += speed_obj.speed_x / now_fps
            speed_obj.y += speed_obj.speed_y / now_fps

        # анимация
        for ani_obj in self.entities.get_with_component(ComAnimated):
            ani_obj.animation_frame_float -= ani_obj.animation_speed / now_fps
            ani_obj.animation_frame = ani_obj.animation_frame_float.__trunc__()  # быстрее int()
            if ani_obj.animation_frame_float < 0.0:
                if ani_obj.animation_looped:
                    ani_obj.animation_frame = len(ani_obj.animation_set.frames) - 1
                    ani_obj.animation_frame_float = float(ani_obj.animation_frame)
                else:
                    self.entities.delete_buffer_add(ani_obj)

        self.entities.delete_buffer_purge()


class SysControl(System):

    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.event_getter: Callable[..., list[Event]] = pygame.event.get
        self.md = None
        self.mouse_event_set = (MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION)

    def start(self):
        self.md = next(self.entities.get_by_class(MenuData))

    def update(self):
        for event in self.event_getter():
            event_type = event.type
            event_key = getattr(event, 'key', None)

            # закрыть
            if event_type == QUIT:
                exit()

            # в корень или выйти из игры
            if event_type == KEYDOWN and event_key in (K_ESCAPE, K_AC_BACK):
                if self.md.scene_active == MENU_SCENE_ROOT:
                    exit()
                else:
                    self.md.scene_active = MENU_SCENE_ROOT

            # gui
            control_button(event, event_type, self.md.scene_active, self.entities)


class SysDraw(System):

    def __init__(self, entities: EntityManager, display: Surface):
        self.entities = entities
        self.display = display
        self.md: Optional[MenuData] = None
        self.background = None
        self.label_game_name = None

    def start(self):
        self.md = next(self.entities.get_by_class(MenuData))
        self.background = next(self.entities.get_by_class(Background))
        self.label_game_name = next(self.entities.get_by_class(LabelGameName))

    def update(self):
        # фон
        self.display.blit(self.background.surface, (self.background.x, self.background.y))
        if self.md.scene_active == MENU_SCENE_ROOT:
            self.display.blit(self.label_game_name.surface, (self.label_game_name.x, self.label_game_name.y))

        # сияние
        if self.md.scene_active == MENU_SCENE_ROOT:
            for shine in self.entities.get_by_class(Shine):
                self.display.blit(shine.animation_set.frames[shine.animation_frame], (shine.x, shine.y))

        # пыль
        for dust in self.entities.get_by_class(Dust):
            self.display.blit(dust.animation_set.frames[dust.animation_frame], (dust.x, dust.y))

        # gui
        draw_text_ml(self.display, self.md.scene_active, self.entities)
        draw_button(self.display, self.md.scene_active, self.entities)
