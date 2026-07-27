from math import ceil
from random import randint
from sys import exit  # *for windows
from time import monotonic, sleep
from typing import Callable, Optional

import pygame
from ecs_pattern import EntityManager, System
from pygame import K_DOWN, K_UP, Rect, Surface
from pygame.event import Event
from pygame.locals import K_AC_BACK, K_ESCAPE, KEYDOWN, QUIT
from pygame.math import Vector2
from pygame.transform import smoothscale

from common_tools.components import ComAnimated, ComSpeed, ComUiCheckbox
from common_tools.consts import (
    FPS_MAX,
    MAIN_SF_HEIGHT_PX,
    MAIN_SF_LEFT_PX,
    MAIN_SF_PADDING_PX,
    MAIN_SF_PROPORTION,
    MAIN_SF_WIDTH_PX,
    MENU_LINE_1_H_COEF,
    MENU_LINE_2_H_COEF,
    MENU_SCENE_ABOUT,
    MENU_SCENE_ROOT,
    MENU_SCENE_SEARCH,
    SCREEN_HEIGHT_PX,
    SCREEN_WIDTH_PX,
    SURFACE_ARGS,
    settings_storage,
)
from common_tools.diafilms_data import choose_random_film, get_selected_films
from common_tools.gui import (
    CS_STATIC,
    PA_SWIPE_DOWN,
    PA_SWIPE_UP,
    PointerEventGetter,
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
from common_tools.math import normal_distribution
from common_tools.resources import (
    FONT_UI_TEXT,
    FONT_UI_TEXT_FOUND,
    IMG_DUST,
    IMG_ICON_ARROW_DOWN,
    IMG_ICON_ARROW_UP,
    IMG_ICON_CLOSE,
    IMG_ICON_DICE,
    IMG_ICON_FLAG_1_DARK,
    IMG_ICON_HOME,
    IMG_ICON_INFO,
    IMG_ICON_PLAY,
    IMG_ICON_SEARCH,
    IMG_ICON_SOUND,
    MUTABLE_RESOURCES,
    SOUND_BUTTON_CLICK,
    SOUND_CHECKBOX_CLICK,
    SOUND_DENY,
    SOUND_MENU,
    SOUND_SHIFT,
    SOUND_START,
    load_frame,
    set_sound_volume,
)
from common_tools.surface import colored_block_surface, colorize_surface, text_surface
from menu.entities import (
    ButtonAbout,
    ButtonExit,
    ButtonHome,
    ButtonPlay,
    ButtonRandomFilm,
    ButtonSearchDo,
    ButtonSearchFilmCard,
    ButtonSearchNextPage,
    ButtonSearchOpen,
    ButtonSearchPrevPage,
    ButtonSearchReset,
    CheckboxAge0Plus,
    CheckboxAge6Plus,
    CheckboxAge12Plus,
    CheckboxCategoryFairyTales,
    CheckboxCategoryNovellasAndStories,
    CheckboxCategoryPoemsAndFables,
    CheckboxChromaBlackWhite,
    CheckboxChromaColor,
    CheckboxSearchByArtist,
    CheckboxSound,
    CheckboxWindowMode,
    Dust,
    DustAnimationSet,
    FrameBorder,
    FrameWhereStopped,
    Header,
    InputSearchFilm,
    MenuBackground,
    MenuData,
    ScrollBarSearch,
    TextAboutFromAuthor,
    TextAboutPlayer,
    TextAboutResources,
    TextSearchFound,
    TextSelectedFilms,
)
from menu.surfaces import (
    surface_dust,
    surface_header,
    surface_main_frame_border,
    surface_main_frame_where_stopped,
    surface_menu_background,
    surface_text_about_from_author,
    surface_text_about_player,
    surface_text_about_resources,
    surface_text_search_found,
    surface_text_selected_films,
)

CHECKBOX_ENT_SET = {
    CheckboxSound,
    CheckboxChromaColor,
    CheckboxChromaBlackWhite,
    CheckboxCategoryNovellasAndStories,
    CheckboxCategoryFairyTales,
    CheckboxCategoryPoemsAndFables,
    CheckboxAge0Plus,
    CheckboxAge6Plus,
    CheckboxAge12Plus,
}


def on_click_button_search_film_card(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    sender: ButtonSearchFilmCard
    # сохраняем настройки
    film = sender.fid
    film_0_frame = MUTABLE_RESOURCES['DIAFILMS_DATA'][film]['frames'][0]
    settings_storage.current_film = film
    settings_storage.current_frame = film_0_frame
    # кадр
    next(entities.get_by_class(FrameWhereStopped)).surface = (
        surface_main_frame_where_stopped(settings_storage.current_film, settings_storage.current_frame))
    # сцена
    next(entities.get_by_class(MenuData)).scene_active = MENU_SCENE_ROOT


def on_click_button_search_do(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_START.play()
    _search(entities)


def on_click_button_search_reset(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    input_ = next(entities.get_by_class(InputSearchFilm))
    input_.text = ''
    input_.state = CS_STATIC
    _search(entities)


def on_click_button_search_next_page(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    scroll = next(entities.get_by_class(ScrollBarSearch))
    if scroll.position_current >= scroll.position_count - 1:
        SOUND_DENY.play()
    else:
        SOUND_SHIFT.play()
        _search(entities, scroll.position_current + 1)


def on_click_button_search_prev_page(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    scroll = next(entities.get_by_class(ScrollBarSearch))
    if scroll.position_current <= 0:
        SOUND_DENY.play()
    else:
        SOUND_SHIFT.play()
        _search(entities, scroll.position_current - 1)


def on_click_button_home(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    next(entities.get_by_class(MenuData)).scene_active = MENU_SCENE_ROOT


def on_click_button_about(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    next(entities.get_by_class(MenuData)).scene_active = MENU_SCENE_ABOUT


def on_click_button_exit(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    sleep(SOUND_BUTTON_CLICK.get_length())
    exit()


def on_click_button_search_open(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    if len(get_selected_films()) == 0:
        SOUND_DENY.play()
        _dust_spawn_no_selected_error(entities)
        return
    SOUND_BUTTON_CLICK.play()
    next(entities.get_by_class(MenuData)).scene_active = MENU_SCENE_SEARCH
    # если текст введен, то не сбрасываем
    if not next(entities.get_by_class(InputSearchFilm)).text:
        _search(entities)


def on_click_button_random_film(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    if len(get_selected_films()) == 0:
        SOUND_DENY.play()
        _dust_spawn_no_selected_error(entities)
        return
    SOUND_BUTTON_CLICK.play()
    choose_random_film()
    next(entities.get_by_class(FrameWhereStopped)).surface = (
        surface_main_frame_where_stopped(settings_storage.current_film, settings_storage.current_frame))


def on_click_button_play(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    if len(get_selected_films()) == 0:
        SOUND_DENY.play()
        _dust_spawn_no_selected_error(entities)
        return
    SOUND_START.play()
    next(entities.get_by_class(MenuData)).do_menu = False


def on_change_checkbox_search_by_artist(sender: ComUiCheckbox, entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_CHECKBOX_CLICK.play()


def on_change_checkbox_window_mode(sender: ComUiCheckbox, entities: EntityManager, pointer_pos: Vector2):  # noqa
    if settings_storage.is_android:
        settings_storage.window_mode = False
        SOUND_DENY.play()
    else:
        settings_storage.window_mode = sender.checked
        SOUND_CHECKBOX_CLICK.play()


def on_change_checkbox_sound(sender: ComUiCheckbox, entities: EntityManager, pointer_pos: Vector2):  # noqa
    settings_storage.sound = sender.checked
    set_sound_volume(sender.checked)
    SOUND_CHECKBOX_CLICK.play()


def on_change_checkbox_chroma_color(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    _film_filters_config_write(entities)
    SOUND_CHECKBOX_CLICK.play()


def on_change_checkbox_chroma_black_white(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    _film_filters_config_write(entities)
    SOUND_CHECKBOX_CLICK.play()


def on_change_checkbox_category_novellas_and_stories(sender: object, entities: EntityManager, p_pos: Vector2):  # noqa
    _film_filters_config_write(entities)
    SOUND_CHECKBOX_CLICK.play()


def on_change_checkbox_category_fairy_tales(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    _film_filters_config_write(entities)
    SOUND_CHECKBOX_CLICK.play()


def on_change_checkbox_category_poems_and_fables(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    _film_filters_config_write(entities)
    SOUND_CHECKBOX_CLICK.play()


def on_change_checkbox_age_0_plus(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    _film_filters_config_write(entities)
    SOUND_CHECKBOX_CLICK.play()


def on_change_checkbox_age_6_plus(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    _film_filters_config_write(entities)
    SOUND_CHECKBOX_CLICK.play()


def on_change_checkbox_age_12_plus(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    _film_filters_config_write(entities)
    SOUND_CHECKBOX_CLICK.play()


def on_change_scrollbar_search(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_SHIFT.play()
    _search(entities, next(entities.get_by_class(ScrollBarSearch)).position_current)


def on_confirm_input_search_film(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_START.play()
    _search(entities)


def on_change_input_search_film(sender: object, entities: EntityManager, pointer_pos: Vector2):  # noqa
    _dust_spawn_at_input_search(entities)


def _dust_spawn(entities: EntityManager):
    """Создать пылинку на произвольной позиции"""
    speed_max = int(MAIN_SF_HEIGHT_PX * 0.04)
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


def _dust_spawn_no_selected_error(entities: EntityManager):
    """Создать пылинки у текста выбранных фильмов, когда выбрано 0 фильмов"""
    text = next(entities.get_by_class(TextSelectedFilms))
    dust = next(entities.get_by_class(DustAnimationSet)).frames[0]
    dd = dust.get_width() // 2  # квадрат
    range_x = (text.rect.x - dd, text.rect.x + text.rect.w - dd)
    range_y = (text.rect.y - dd, text.rect.y + text.rect.h - dd)
    speed_max = int(MAIN_SF_HEIGHT_PX * 0.05)
    frame = 128  # из 255
    for i in range(20):
        entities.add(
            Dust(
                animation_set=next(entities.get_by_class(DustAnimationSet)),
                animation_looped=False,
                animation_frame=frame,
                animation_frame_float=float(frame),
                animation_speed=randint(10, 50),
                x=randint(*range_x),
                y=randint(*range_y),
                speed_x=randint(-speed_max, speed_max),
                speed_y=randint(-speed_max, speed_max),
            )
        )


def _dust_spawn_at_input_search(entities: EntityManager):
    """Создать пылинки у инпута для поиска фильмов"""
    # не слишком часто (скролл)
    menu_data = next(entities.get_by_class(MenuData))
    now_time = monotonic()
    if now_time - menu_data.search_dust_last_time < 1:
        return
    menu_data.search_dust_last_time = now_time

    input_ = next(entities.get_by_class(InputSearchFilm))
    dust = next(entities.get_by_class(DustAnimationSet)).frames[0]
    dd = dust.get_width() // 2  # квадрат
    range_x = (input_.rect.x - dd, input_.rect.x + input_.rect.w)
    range_y = (input_.rect.y - dd, input_.rect.y + input_.rect.h)
    speed_max = int(MAIN_SF_HEIGHT_PX * 0.1)
    frame = 128  # из 255
    for i in range(40):
        entities.add(
            Dust(
                animation_set=next(entities.get_by_class(DustAnimationSet)),
                animation_looped=False,
                animation_frame=frame,
                animation_frame_float=float(frame),
                animation_speed=randint(10, 50),
                x=randint(*range_x),
                y=randint(*range_y),
                speed_x=randint(-speed_max, speed_max),
                speed_y=randint(-speed_max, speed_max),
            )
        )


# привязка фильтров settings_storage.film_filters к чекбоксам
_film_filters_config_map = {
    0: CheckboxChromaColor,
    1: CheckboxChromaBlackWhite,
    2: CheckboxCategoryNovellasAndStories,
    3: CheckboxCategoryFairyTales,
    4: CheckboxCategoryPoemsAndFables,
    5: CheckboxAge0Plus,
    6: CheckboxAge6Plus,
    7: CheckboxAge12Plus,
}


def _film_filters_config_read(entities: EntityManager):
    """Чтение конфигурации фильтрации фильмов, отображение данных в GUI"""
    for film_filter_i, film_filter_val in enumerate(settings_storage.film_filters):
        filter_check_box_class = _film_filters_config_map[film_filter_i]
        next(entities.get_by_class(filter_check_box_class)).checked = film_filter_val
    next(entities.get_by_class(TextSelectedFilms)).sf_text = (
        surface_text_selected_films(len(get_selected_films()), len(MUTABLE_RESOURCES['DIAFILMS_DATA'])))


def _film_filters_config_write(entities: EntityManager):
    """Запись текущей в GUI конфигурации фильтрации фильмов"""
    vals_for_write: list[bool] = []
    for filter_check_box_class in _film_filters_config_map.values():
        vals_for_write.append(next(entities.get_by_class(filter_check_box_class)).checked)
    settings_storage.film_filters = vals_for_write
    next(entities.get_by_class(TextSelectedFilms)).sf_text = (
        surface_text_selected_films(len(get_selected_films()), len(MUTABLE_RESOURCES['DIAFILMS_DATA'])))
    next(entities.get_by_class(InputSearchFilm)).text = ''


def _search(entities: EntityManager, scroll_position_current: int = 0):
    """
    Поиск по выбранным диафильмам, отображение 8 ButtonSearchFilmCard
    :param entities: EntityManager
    :param scroll_position_current: с указанной позиции scroll_position_current (текущая страница)
    """
    # пылинки
    _dust_spawn_at_input_search(entities)

    # удаляем старые кнопки
    for ent in entities.get_by_class(ButtonSearchFilmCard):
        entities.delete_buffer_add(ent)
    entities.delete_buffer_purge()

    # поиск фильмов
    selected_films = get_selected_films()  # fids
    search_text = next(entities.get_by_class(InputSearchFilm)).text.lower()
    is_search_by_artist = next(entities.get_by_class(CheckboxSearchByArtist)).checked
    search_field = 'artist' if is_search_by_artist else 'name'
    found_films = {
        k: v for k, v in MUTABLE_RESOURCES['DIAFILMS_DATA'].items()
        if search_text in v[search_field].lower() and k in selected_films
    }

    # при смене текста поиска без нажатия поиск - предполагается новый поиск
    menu_data = next(entities.get_by_class(MenuData))
    if menu_data.search_text_last.lower() != search_text:
        scroll_position_current = 0
    menu_data.search_text_last = search_text

    # обновляем текст
    next(entities.get_by_class(TextSearchFound)).sf_text = (
        surface_text_search_found(search_text, is_search_by_artist, len(found_films), len(selected_films)))

    # обновляем скролл
    scroll = next(entities.get_by_class(ScrollBarSearch))
    if len(found_films) == 0:
        scroll.position_count = 1
        scroll.position_current = scroll.position_future = 0
        return
    scroll.position_count = max(ceil(len(found_films) / 8), 1)  # количество страниц: 1-X
    scroll.position_current = scroll.position_future = scroll_position_current  # с нуля

    # создаем новые кнопки ButtonSearchFilmCard
    btn_small_rect: Rect = menu_data.btn_small_rect
    _cw = (MAIN_SF_WIDTH_PX / 2 - MAIN_SF_PADDING_PX * 3 - btn_small_rect.width) * 0.98
    _ch = _cw * MAIN_SF_PROPORTION / 2  # 2 кадра
    _col1_x = MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX / 2 - _cw - MAIN_SF_PADDING_PX * 0.5
    _col2_x = MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX / 2 + MAIN_SF_PADDING_PX * 0.5
    _pad_y = btn_small_rect.height + MAIN_SF_PADDING_PX * 3
    card_rects = [
        Rect(_col1_x, _pad_y + _ch * 0 + MAIN_SF_PADDING_PX * 0, _cw, _ch),
        Rect(_col1_x, _pad_y + _ch * 1 + MAIN_SF_PADDING_PX * 1, _cw, _ch),
        Rect(_col1_x, _pad_y + _ch * 2 + MAIN_SF_PADDING_PX * 2, _cw, _ch),
        Rect(_col1_x, _pad_y + _ch * 3 + MAIN_SF_PADDING_PX * 3, _cw, _ch),
        Rect(_col2_x, _pad_y + _ch * 0 + MAIN_SF_PADDING_PX * 0, _cw, _ch),
        Rect(_col2_x, _pad_y + _ch * 1 + MAIN_SF_PADDING_PX * 1, _cw, _ch),
        Rect(_col2_x, _pad_y + _ch * 2 + MAIN_SF_PADDING_PX * 2, _cw, _ch),
        Rect(_col2_x, _pad_y + _ch * 3 + MAIN_SF_PADDING_PX * 3, _cw, _ch),
    ]
    rect_i = 0
    for i, fid in enumerate(found_films):
        # фильмы только с выбранной страница поиска
        if i // 8 != scroll_position_current:
            continue

        card_rect = card_rects[rect_i]  # (x left, y top, w width, h height)
        # подложка
        frame_sf_h = card_rect.height
        frame_sf_w = card_rect.width / 2

        # 1й и 2й кадры
        frame1_sf = smoothscale(
            load_frame(fid, found_films[fid]["frames"][0]).convert_alpha(), (frame_sf_w, frame_sf_h))
        frame2_sf = smoothscale(
            load_frame(fid, found_films[fid]["frames"][1]).convert_alpha(), (frame_sf_w, frame_sf_h))

        card_sf = Surface((card_rect.width, card_rect.height), **SURFACE_ARGS)
        card_sf.blit(frame1_sf, (0, 0))
        card_sf.blit(frame2_sf, (frame_sf_w, 0))

        # текст
        # f'{i + 1}. {found_films[fid]["name"]}'
        text_sf = text_surface(FONT_UI_TEXT_FOUND, f'{i + 1}.', '#222222', '#eeeeee')
        card_sf.blit(text_sf, (5, 0))

        # поверхности
        sf_static = card_sf
        sf_hover = colorize_surface(card_sf, '#ffe076')
        sf_pressed = colorize_surface(card_sf, '#a9ffde')
        entities.add(
            ButtonSearchFilmCard(
                fid=fid,
                scenes=[MENU_SCENE_SEARCH],
                on_click=on_click_button_search_film_card,
                state=CS_STATIC,
                sf_hover=sf_hover,
                sf_pressed=sf_pressed,
                sf_static=sf_static,
                mask=pygame.mask.from_surface(sf_static),
                rect=card_rect,
            )
        )

        rect_i += 1


class SysInit(System):

    def __init__(self, entities: EntityManager):
        self.entities = entities

    def start(self):
        set_sound_volume(settings_storage.sound)

        _pixel_sf = colored_block_surface('red', 1, 1)

        self.entities.init(
            Dust([], False, 0, 0, 0, 0, 0, 0, 0),
            ButtonSearchFilmCard(fid='1', scenes=[0], on_click=0, **make_attrs_button(x=1, y=2, icon=_pixel_sf)),
        )
        # пылинки
        normal_dist_data = normal_distribution(list(range(256)), 128, 10)
        normal_dist_max_val = max(normal_dist_data)
        dust_alpha_dist = [int(i * 255 / normal_dist_max_val) for i in normal_dist_data]

        # начало линий (сверху вниз)
        _line_1_y = 0
        _line_2_y = MAIN_SF_HEIGHT_PX * MENU_LINE_1_H_COEF
        _line_3_y = MAIN_SF_HEIGHT_PX * (MENU_LINE_1_H_COEF + MENU_LINE_2_H_COEF)

        # маленькая кнопка
        _btn_small = ButtonPlay(
            scenes=[0], on_click=None, **make_attrs_button(0, 0, _pixel_sf))
        _btn_small_w_px = _btn_small.rect.width
        _btn_small_h_px = _btn_small.rect.height
        _btn_small_pad_px = _btn_small_h_px * 0.33

        # Х первой колонки ButtonSearchFilmCard
        __cw = (MAIN_SF_WIDTH_PX / 2 - MAIN_SF_PADDING_PX * 3 - _btn_small_w_px) * 0.98
        film_card_col1_x = MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX / 2 - __cw - MAIN_SF_PADDING_PX * 0.5

        # чекбокс - линия 2
        _chb_l2 = CheckboxChromaColor(scenes=[0], checked=True, on_change=None, **make_attrs_checkbox(0, 0, ''))
        _chb_l2_w_px = _chb_l2.rect.width
        _chb_l2_h_px = _chb_l2.rect.height
        _line_2_chb_pad = _chb_l2_h_px * 0.22

        # большая кнопка - линия 3
        _btn_big = ButtonPlay(
            scenes=[0], on_click=None, **make_attrs_button(0, 0, _pixel_sf, 'big'))
        _btn_big_w_px = _btn_big.rect.width
        _btn_big_h_px = _btn_big.rect.height
        _line_3_btn_pad = _btn_big_h_px * 0.58

        # инпут
        _input = InputSearchFilm(
            scenes=[0], max_length=0, text='', on_confirm=None, on_change=None, **make_attrs_input(0, 0, ''))
        _input_w_px = _input.rect.width
        _input_h_px = _input.rect.height

        # скролл
        _scroll = ScrollBarSearch(scenes=[0], on_change=None, position_count=5, position_current=0, position_future=0,
                                  **make_attrs_scroll(0, 0, height=MAIN_SF_HEIGHT_PX - MAIN_SF_PADDING_PX * 2))
        _scroll_w_px = _scroll.rect.width
        _scroll_h_px = _scroll.rect.height

        # о программе
        _txt_about = TextAboutPlayer(scenes=[0], **make_attrs_text(0, 0, surface_text_about_player()))
        _txt_about_w = _txt_about.rect.width

        # кадр
        _surface_main_frame_where_stopped = surface_main_frame_where_stopped(
            settings_storage.current_film, settings_storage.current_frame)
        _surface_main_frame_border = surface_main_frame_border()

        self.entities.add(
            # общее
            MenuData(
                do_menu=True,
                scene_active=MENU_SCENE_ROOT,
                music_channel=SOUND_MENU.play(-1),
                last_dust_spawn_time=0.0,
                btn_small_rect=_btn_small.rect,
                search_text_last='',
                search_dust_last_time=0.0,
            ),
            DustAnimationSet(
                tuple(surface_dust(IMG_DUST, i) for i in dust_alpha_dist)
            ),
            MenuBackground(
                x=0,
                y=0,
                surface=surface_menu_background(),
            ),
            ButtonHome(
                scenes=[MENU_SCENE_SEARCH, MENU_SCENE_ABOUT],
                on_click=on_click_button_home,
                **make_attrs_button(
                    x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX - MAIN_SF_PADDING_PX - _btn_small_w_px,
                    y=MAIN_SF_PADDING_PX,
                    icon=IMG_ICON_HOME,
                ),
            ),

            # MENU_SCENE_ROOT ==========================================================================================
            Header(
                x=MAIN_SF_LEFT_PX,
                y=0,
                surface=surface_header(),
            ),
            CheckboxWindowMode(
                scenes=[-1 if settings_storage.is_android else MENU_SCENE_ROOT],
                checked=settings_storage.window_mode,
                on_change=on_change_checkbox_window_mode,
                **make_attrs_checkbox(
                    x=MAIN_SF_LEFT_PX,
                    y=MAIN_SF_HEIGHT_PX - MAIN_SF_PADDING_PX - _btn_big_h_px * 3 - _line_3_btn_pad * 3
                      - _chb_l2_h_px * 1.04,
                    text='Запуск в окне',
                    icon1=IMG_ICON_FLAG_1_DARK,
                    scale_w=0.75,
                    scale_h=1.38
                ),
            ),
            CheckboxSound(
                scenes=[MENU_SCENE_ROOT],
                checked=settings_storage.sound,
                on_change=on_change_checkbox_sound,
                **make_attrs_checkbox(
                    x=MAIN_SF_LEFT_PX,
                    y=MAIN_SF_HEIGHT_PX - MAIN_SF_PADDING_PX - _btn_big_h_px * 3 - _line_3_btn_pad * 3,
                    text='Звук',
                    icon1=IMG_ICON_SOUND,
                    scale_w=0.75,
                    scale_h=1.38
                ),
            ),
            ButtonAbout(
                scenes=[MENU_SCENE_ROOT],
                on_click=on_click_button_about,
                **make_attrs_button(
                    x=MAIN_SF_LEFT_PX,
                    y=MAIN_SF_HEIGHT_PX - MAIN_SF_PADDING_PX - _btn_big_h_px * 2 - _line_3_btn_pad * 2,
                    text='О программе',
                    icon=IMG_ICON_INFO,
                ),
            ),
            ButtonExit(
                scenes=[MENU_SCENE_ROOT],
                on_click=on_click_button_exit,
                **make_attrs_button(
                    x=MAIN_SF_LEFT_PX,
                    y=MAIN_SF_HEIGHT_PX - MAIN_SF_PADDING_PX - _btn_big_h_px * 1 - _line_3_btn_pad * 1,
                    text='Выход',
                    icon=IMG_ICON_CLOSE,
                ),
            ),
            ButtonPlay(
                scenes=[MENU_SCENE_ROOT],
                on_click=on_click_button_play,
                **make_attrs_button(
                    x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX - _btn_big_w_px,
                    y=MAIN_SF_HEIGHT_PX - MAIN_SF_PADDING_PX - _btn_big_h_px * 3 - _line_3_btn_pad * 3,
                    text='Смотреть',
                    icon=IMG_ICON_PLAY,
                ),
            ),
            ButtonSearchOpen(
                scenes=[MENU_SCENE_ROOT],
                on_click=on_click_button_search_open,
                **make_attrs_button(
                    x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX - _btn_big_w_px,
                    y=MAIN_SF_HEIGHT_PX - MAIN_SF_PADDING_PX - _btn_big_h_px * 2 - _line_3_btn_pad * 2,
                    text='Поиск',
                    icon=IMG_ICON_SEARCH,
                ),
            ),
            ButtonRandomFilm(
                scenes=[MENU_SCENE_ROOT],
                on_click=on_click_button_random_film,
                **make_attrs_button(
                    x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX - _btn_big_w_px,
                    y=MAIN_SF_HEIGHT_PX - MAIN_SF_PADDING_PX - _btn_big_h_px * 1 - _line_3_btn_pad * 1,
                    text='Случайный',
                    icon=IMG_ICON_DICE,
                ),
            ),
            #
            CheckboxCategoryNovellasAndStories(
                scenes=[MENU_SCENE_ROOT],
                checked=True,
                on_change=on_change_checkbox_category_novellas_and_stories,
                **make_attrs_checkbox(
                    x=MAIN_SF_LEFT_PX,
                    y=_line_2_y + _chb_l2_h_px * 0 + _line_2_chb_pad * 1,
                    text='Повести и рассказы',
                ),
            ),
            CheckboxCategoryFairyTales(
                scenes=[MENU_SCENE_ROOT],
                checked=True,
                on_change=on_change_checkbox_category_fairy_tales,
                **make_attrs_checkbox(
                    x=MAIN_SF_LEFT_PX,
                    y=_line_2_y + _chb_l2_h_px * 1 + _line_2_chb_pad * 2,
                    text='Сказки',
                ),
            ),
            CheckboxCategoryPoemsAndFables(
                scenes=[MENU_SCENE_ROOT],
                checked=True,
                on_change=on_change_checkbox_category_poems_and_fables,
                **make_attrs_checkbox(
                    x=MAIN_SF_LEFT_PX,
                    y=_line_2_y + _chb_l2_h_px * 2 + _line_2_chb_pad * 3,
                    text='Стихи и басни',
                ),
            ),
            CheckboxChromaColor(
                scenes=[MENU_SCENE_ROOT],
                checked=True,
                on_change=on_change_checkbox_chroma_color,
                **make_attrs_checkbox(
                    x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX / 2 - _chb_l2_w_px / 2,
                    y=_line_2_y + _chb_l2_h_px * 0 + _line_2_chb_pad * 1,
                    text='Цветной',
                ),
            ),
            CheckboxChromaBlackWhite(
                scenes=[MENU_SCENE_ROOT],
                checked=True,
                on_change=on_change_checkbox_chroma_black_white,
                **make_attrs_checkbox(
                    x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX / 2 - _chb_l2_w_px / 2,
                    y=_line_2_y + _chb_l2_h_px * 1 + _line_2_chb_pad * 2,
                    text='Чёрно-белый',
                ),
            ),
            CheckboxAge0Plus(
                scenes=[MENU_SCENE_ROOT],
                checked=True,
                on_change=on_change_checkbox_age_0_plus,
                **make_attrs_checkbox(
                    x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX - _chb_l2_w_px,
                    y=_line_2_y + _chb_l2_h_px * 0 + _line_2_chb_pad * 1,
                    text='Возраст 0+',
                ),
            ),
            CheckboxAge6Plus(
                scenes=[MENU_SCENE_ROOT],
                checked=True,
                on_change=on_change_checkbox_age_6_plus,
                **make_attrs_checkbox(
                    x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX - _chb_l2_w_px,
                    y=_line_2_y + _chb_l2_h_px * 1 + _line_2_chb_pad * 2,
                    text='Возраст 6+',
                ),
            ),
            CheckboxAge12Plus(
                scenes=[MENU_SCENE_ROOT],
                checked=True,
                on_change=on_change_checkbox_age_12_plus,
                **make_attrs_checkbox(
                    x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX - _chb_l2_w_px,
                    y=_line_2_y + _chb_l2_h_px * 2 + _line_2_chb_pad * 3,
                    text='Возраст 12+',
                ),
            ),
            #
            TextSelectedFilms(
                scenes=[MENU_SCENE_ROOT],
                **make_attrs_text(
                    x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX / 2 - FONT_UI_TEXT.size('A')[0] * 7,
                    y=_line_2_y + _chb_l2_h_px * 2.22 + _line_2_chb_pad * 3,
                    sf=surface_text_selected_films(108, 2317),
                )
            ),
            #
            FrameWhereStopped(
                x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX / 2 - _surface_main_frame_where_stopped.get_width() / 2,
                y=_line_3_y,
                surface=_surface_main_frame_where_stopped,
            ),
            FrameBorder(
                x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX / 2 - _surface_main_frame_border.get_width() / 2,
                y=_line_3_y,
                surface=_surface_main_frame_border,
            ),

            # MENU_SCENE_ABOUT =========================================================================================
            TextAboutPlayer(
                scenes=[MENU_SCENE_ABOUT],
                **make_attrs_text(
                    x=MAIN_SF_LEFT_PX + _txt_about_w * 0,
                    y=0,
                    sf=surface_text_about_player(),
                )
            ),
            TextAboutResources(
                scenes=[MENU_SCENE_ABOUT],
                **make_attrs_text(
                    x=MAIN_SF_LEFT_PX + _txt_about_w * 1,
                    y=0,
                    sf=surface_text_about_resources(),
                )
            ),
            TextAboutFromAuthor(
                scenes=[MENU_SCENE_ABOUT],
                **make_attrs_text(
                    x=MAIN_SF_LEFT_PX + _txt_about_w * 2,
                    y=0,
                    sf=surface_text_about_from_author(),
                )
            ),

            # MENU_SCENE_SEARCH ========================================================================================
            CheckboxSearchByArtist(
                scenes=[MENU_SCENE_SEARCH],
                checked=False,
                on_change=on_change_checkbox_search_by_artist,
                **make_attrs_checkbox(
                    x=film_card_col1_x,
                    y=MAIN_SF_PADDING_PX * 1.25,
                    text='По художнику',
                    icon1=IMG_ICON_FLAG_1_DARK,
                    scale_w=0.75,
                    scale_h=1.38
                ),
            ),

            ButtonSearchDo(
                scenes=[MENU_SCENE_SEARCH],
                on_click=on_click_button_search_do,
                **make_attrs_button(
                    x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX / 2 + _input_w_px / 2 + MAIN_SF_PADDING_PX * 2.2,
                    y=MAIN_SF_PADDING_PX,
                    icon=IMG_ICON_SEARCH,
                ),
            ),
            ButtonSearchReset(
                scenes=[MENU_SCENE_SEARCH],
                on_click=on_click_button_search_reset,
                **make_attrs_button(
                    x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX / 2 + _input_w_px / 2
                      + _btn_small_w_px + MAIN_SF_PADDING_PX * 3.2,
                    y=MAIN_SF_PADDING_PX,
                    icon=IMG_ICON_CLOSE,
                ),
            ),
            ButtonSearchPrevPage(
                scenes=[MENU_SCENE_SEARCH],
                on_click=on_click_button_search_prev_page,
                **make_attrs_button(
                    x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX - MAIN_SF_PADDING_PX - _btn_small_w_px,
                    y=MAIN_SF_HEIGHT_PX / 2 - _btn_small_pad_px - _btn_small_h_px,
                    icon=IMG_ICON_ARROW_UP,
                ),
            ),
            ButtonSearchNextPage(
                scenes=[MENU_SCENE_SEARCH],
                on_click=on_click_button_search_next_page,
                **make_attrs_button(
                    x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX - MAIN_SF_PADDING_PX - _btn_small_w_px,
                    y=MAIN_SF_HEIGHT_PX / 2,
                    icon=IMG_ICON_ARROW_DOWN,
                ),
            ),
            #
            ScrollBarSearch(
                scenes=[MENU_SCENE_SEARCH],
                on_change=on_change_scrollbar_search,
                position_count=15,
                position_current=0,
                position_future=0,
                **make_attrs_scroll(
                    x=MAIN_SF_LEFT_PX + MAIN_SF_PADDING_PX,
                    y=MAIN_SF_PADDING_PX,
                    height=MAIN_SF_HEIGHT_PX - MAIN_SF_PADDING_PX * 2
                ),
            ),
            InputSearchFilm(
                scenes=[MENU_SCENE_SEARCH],
                max_length=20,
                text='',
                on_confirm=on_confirm_input_search_film,
                on_change=on_change_input_search_film,
                **make_attrs_input(
                    x=MAIN_SF_LEFT_PX + MAIN_SF_WIDTH_PX / 2 - _input_w_px / 2 + MAIN_SF_PADDING_PX * 0.7,
                    y=MAIN_SF_PADDING_PX * 0.8,
                    placeholder='Поиск диафильмов',
                )
            ),
            TextSearchFound(
                scenes=[MENU_SCENE_SEARCH],
                **make_attrs_text(
                    x=film_card_col1_x,
                    y=MAIN_SF_PADDING_PX * 1.2 + _btn_small_h_px,
                    sf=surface_text_search_found('', False, 37, 1300),
                )
            ),
        )
        _film_filters_config_read(self.entities)

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
        if now_time - self.md.last_dust_spawn_time > 0.4:  # скорость 1 раз в 0.5сек - около 15 одновременных пылинок
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
    def __init__(self, entities: EntityManager):  # noqa
        self.entities = entities
        self.event_getter: Callable[..., list[Event]] = pygame.event.get
        self.md = None
        self.pointer_event_getter = None

    def start(self):
        self.md = next(self.entities.get_by_class(MenuData))
        self.pointer_event_getter = PointerEventGetter()

    def update(self):
        for event in self.event_getter():
            event_type = event.type
            event_key = getattr(event, 'key', None)

            # закрыть окно
            if event_type == QUIT:
                exit()

            # ескейп или назад на андроид
            if event_type == KEYDOWN and event_key in (K_ESCAPE, K_AC_BACK):
                if self.md.scene_active != MENU_SCENE_ROOT:
                    self.md.scene_active = MENU_SCENE_ROOT
                else:
                    exit()

            # управление поиском
            pointer_action = self.pointer_event_getter.get_pointer_action(event)
            if self.md.scene_active == MENU_SCENE_SEARCH:
                if pointer_action == PA_SWIPE_UP or event_type == KEYDOWN and event_key == K_DOWN:
                    on_click_button_search_next_page(None, self.entities, Vector2(0, 0))
                if pointer_action == PA_SWIPE_DOWN or event_type == KEYDOWN and event_key == K_UP:
                    on_click_button_search_prev_page(None, self.entities, Vector2(0, 0))

            # gui
            if control_button(event, event_type, self.md.scene_active, self.entities):
                continue
            if control_checkbox(event, event_type, self.md.scene_active, self.entities):
                continue
            if control_scroll(event, event_type, self.md.scene_active, self.entities):
                continue
            control_input_activate(event, event_type, self.md.scene_active, self.entities)
            control_input_edit(event, event_type, event_key, self.md.scene_active, self.entities)


class SysDraw(System):
    def __init__(self, entities: EntityManager, display: Surface):
        self.entities = entities
        self.display = display
        self.md: Optional[MenuData] = None
        self.header = None

    def start(self):
        self.md = next(self.entities.get_by_class(MenuData))
        self.header = next(self.entities.get_by_class(Header))

    def update(self):
        # background
        for with_sf in self.entities.get_by_class(MenuBackground):
            self.display.blit(with_sf.surface, (with_sf.x, with_sf.y))

        # with_sf
        if self.md.scene_active == MENU_SCENE_ROOT:
            for with_sf in self.entities.get_by_class(FrameWhereStopped, FrameBorder, Header):
                self.display.blit(with_sf.surface, (with_sf.x, with_sf.y))

        # пыль
        for dust in self.entities.get_by_class(Dust):
            self.display.blit(dust.animation_set.frames[dust.animation_frame], (dust.x, dust.y))

        # gui
        draw_text(self.display, self.md.scene_active, self.entities)
        draw_button(self.display, self.md.scene_active, self.entities)
        draw_input(self.display, self.md.scene_active, self.entities)
        draw_checkbox(self.display, self.md.scene_active, self.entities)
        draw_scroll(self.display, self.md.scene_active, self.entities)
