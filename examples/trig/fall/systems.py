from functools import cache
from random import choice, randint
from sys import exit  # *for windows
from time import monotonic, sleep
from typing import Callable, Optional, Tuple

import pygame
from ecs_pattern import EntityManager, System
from pygame import Rect, Surface
from pygame.event import Event
from pygame.locals import (
    K_AC_BACK,
    K_DOWN,
    K_ESCAPE,
    K_LEFT,
    K_LSHIFT,
    K_RIGHT,
    K_RSHIFT,
    K_SPACE,
    K_UP,
    KEYDOWN,
    KEYUP,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    QUIT,
)
from pygame.math import Vector2
from pygame.transform import scale

from common_tools.build_flags import PACKAGE_EDITION
from common_tools.components import ComAnimated, ComAnimationSet, ComLiveTime, ComSpeed
from common_tools.consts import (
    BUTTON_WIDTH,
    DIR_ARROW_ALPHA,
    EVENT_NO_INTERSECT_CHANCE,
    EVENT_SCORE_CHANCE,
    EVENT_SCORE_RANGE,
    EVENT_SCORE_SMALL_CHANCE,
    EVENT_SCORE_SMALL_RANGE,
    FALL_SCENE_GAME_OVER,
    FALL_SCENE_PAUSE,
    FALL_SCENE_PLAY,
    FIGURE_CENTER_PAD,
    FIGURE_COLS,
    FIGURE_ROW_COL,
    FIGURE_ROWS,
    FIGURES,
    FPS_MAX,
    GRID_COLS,
    GRID_HIDDEN_TOP_ROWS,
    GRID_MARGIN_HOR,
    GRID_MARGIN_VER,
    GRID_ROWS,
    GRID_TRI_GAP_COL,
    GRID_TRI_GAP_ROW,
    GRID_TRI_HEIGHT,
    GRID_TRI_WIDTH,
    GRID_TRI_Y_CORR,
    INFO_AREA_HEIGHT,
    INFO_AREA_WIDTH,
    IS_ACTIVE,
    IS_STATIC,
    MATRIX_COLS,
    MATRIX_ROW_COL,
    MATRIX_ROWS,
    PA_MOVE_FAST,
    PA_MOVE_LEFT,
    PA_MOVE_RIGHT,
    PA_ROTATE,
    PA_SWITCH_DIR,
    PACKAGE_EDITION_FREE,
    PLAY_AREA_HEIGHT,
    PLAY_AREA_PADDING,
    PLAY_AREA_WIDTH,
    PLUS_MINUS_ONE,
    SCORE_MAP,
    SCREEN_HEIGHT_PX,
    SCREEN_WIDTH_PX,
    SETTINGS_STORAGE,
    SPARK_SIZE_PX,
    SPEED_FAST_FALL,
    SPEED_FAST_FALL_CNT,
    SPEED_MAP,
)
from common_tools.gui import (
    control_button,
    control_input_activate,
    control_input_edit,
    draw_button,
    draw_input,
    draw_text_ml,
    gui_button_attrs,
)
from common_tools.i18n import I18N_FALL_EXIT_GAME, I18N_FALL_RESUME_GAME, I18N_FALL_SAVE_RESULT, I18N_FALL_TO_MAIN_MENU
from common_tools.math import polar2cart
from common_tools.matrix import m_2d_move, m_create, m_del_rows, m_expand, m_intersects, m_is_sum_equals, m_trim
from common_tools.resources import (
    FONT_SCORE_HEIGHT_PX,
    FONT_SPEED_HEIGHT_PX,
    FONT_TEXT_ML,
    IMG_SPARK_DARK,
    IMG_SPARK_LIGHT,
    SOUND_BUTTON_CLICK,
    SOUND_CHANGE_DIR,
    SOUND_CLEAN_LINE,
    SOUND_EVENT_NO_INTERSECT,
    SOUND_FAST_FALL,
    SOUND_FIGURE_DROP,
    SOUND_GAME_OVER,
    SOUND_GAME_SPEED_UP,
    SOUND_PAUSE,
    SOUND_ROTATE,
    SOUND_SCORE,
    SOUND_SHIFT,
    SOUND_TEXT_INPUT,
    set_sound_volume,
)
from common_tools.surface import colored_block_surface

from .entities import (
    Border,
    ButtonExitGame,
    ButtonResumeGame,
    ButtonSaveResult,
    ButtonToMainMenu,
    DirectionArrowLeft,
    DirectionArrowRight,
    FullScreenFlash,
    GameData,
    IconNextFigure,
    InfoArea,
    InputPlayerName,
    LabelGameOver,
    LabelPause,
    Loading,
    PlayArea,
    Spark,
    SparkDel1AnimationSet,
    SparkDel2AnimationSet,
    TextGameResults,
    TextScore,
    TextScorePopup,
    TextSpeed,
    TextSpeedPopup,
    TextStartGameGreetPopup,
    TriangleActiveDown,
    TriangleActiveUp,
    TriangleGridDown,
    TriangleGridUp,
    TriangleNoIntersectDown,
    TriangleNoIntersectUp,
    TriangleScoreDown,
    TriangleScoreDownSmall,
    TriangleScoreUp,
    TriangleScoreUpSmall,
    TriangleStaticDown,
    TriangleStaticUp,
)
from .surfaces import (
    surface_border,
    surface_direction_arrow_left,
    surface_direction_arrow_right,
    surface_full_screen_flash,
    surface_info_area,
    surface_input_player_name,
    surface_label_game_over,
    surface_label_pause,
    surface_loading,
    surface_play_area,
    surface_spark,
    surface_text_game_results,
    surface_text_score,
    surface_text_speed,
    surface_text_speed_popup,
    surface_text_start_game_greet_popup,
    surface_triangle_active_down,
    surface_triangle_active_up,
    surface_triangle_grid_down,
    surface_triangle_grid_up,
    surface_triangle_no_intersect_down,
    surface_triangle_no_intersect_up,
    surface_triangle_score_down,
    surface_triangle_score_down_small,
    surface_triangle_score_up,
    surface_triangle_score_up_small,
    surface_triangle_static_down,
    surface_triangle_static_up,
)


def _get_random_figure_variant() -> Tuple[int, int]:
    """Случайный вариант фигуры - (номер фигуры, вариант фигуры)"""
    figure_next_set = randint(0, len(FIGURES) - 1)
    figure_next_variant = randint(0, len(FIGURES[figure_next_set]) - 1)
    # return 4, 0  # треугольник
    # return 7, 3  # полукруг
    return figure_next_set, figure_next_variant


@cache
def _is_tri_oriented_down(row: int, col: int) -> bool:
    """Ориентирован ли треугольник с заданными координатами вершиной вниз"""
    return bool((row + col) % 2)


@cache
def _get_tri_coord(row: int, col: int, flip: bool) -> tuple[float, float]:
    """Координаты треугольника на дисплее - (x, y)"""
    if not (row >= 0 and col >= 0):
        raise ValueError
    return (
        SCREEN_WIDTH_PX * (
                PLAY_AREA_PADDING + GRID_MARGIN_HOR + GRID_TRI_WIDTH / 2 * col + GRID_TRI_GAP_COL * (col - 1)
        ),
        SCREEN_HEIGHT_PX * (
                PLAY_AREA_PADDING + GRID_MARGIN_VER + GRID_TRI_HEIGHT * row + GRID_TRI_GAP_ROW * (row - 1) +
                INFO_AREA_HEIGHT + GRID_TRI_Y_CORR * (-1 if flip else 1)
        )
    )


@cache
def _get_figure_dir_coord(row: int, col: int, flip: bool) -> tuple[float, float]:
    """Координаты стрелки направления движения фигуры на треугольнике - (x, y)"""
    if not (row >= 0 and col >= 0):
        raise ValueError
    tw = int(SCREEN_WIDTH_PX * GRID_TRI_WIDTH)
    th = int(SCREEN_HEIGHT_PX * GRID_TRI_HEIGHT)
    cx, cy = _get_tri_center(row, col, flip)
    h_fx = th * 0.15 * (-1 if flip else 1)
    return cx - int(tw / 2), cy - int(th / 2) + h_fx


@cache
def _get_tri_center(row: int, col: int, flip: bool) -> tuple[float, float]:
    """Координаты центра треугольника на дисплее"""
    x, y = _get_tri_coord(row, col, flip)
    return x + SCREEN_WIDTH_PX * GRID_TRI_WIDTH / 2, y + SCREEN_HEIGHT_PX * GRID_TRI_HEIGHT / 2


def _surface_icon_next_figure(
        figure_next: Tuple[int, int], tri_active_up: Surface, tri_active_down: Surface) -> Surface:
    full_w = int(SCREEN_WIDTH_PX * (GRID_TRI_WIDTH / 2 * (FIGURE_COLS + 1) + GRID_TRI_GAP_COL * (FIGURE_COLS - 1)))
    full_h = int(SCREEN_HEIGHT_PX * (GRID_TRI_HEIGHT * FIGURE_ROWS + GRID_TRI_GAP_ROW * (FIGURE_ROWS - 1)))
    surface = colored_block_surface(0, full_w, full_h)
    figure = FIGURES[figure_next[0]][figure_next[1]]
    # figure = ((1, 1, 1, 1, 1), (1, 1, 1, 1, 1), (1, 1, 1, 1, 1),)
    for row, col in FIGURE_ROW_COL:
        if figure[row][col]:
            flip = _is_tri_oriented_down(row, col)
            tri_coord = _get_tri_coord(row, col, flip)
            surface.blit(
                tri_active_down if flip else tri_active_up,
                (
                    tri_coord[0] - SCREEN_WIDTH_PX * (
                            PLAY_AREA_PADDING + GRID_MARGIN_HOR - GRID_TRI_GAP_COL),
                    tri_coord[1] - SCREEN_HEIGHT_PX * (
                            INFO_AREA_HEIGHT + PLAY_AREA_PADDING + GRID_MARGIN_VER - GRID_TRI_GAP_ROW)
                )
            )
    ia_h = SCREEN_HEIGHT_PX * INFO_AREA_HEIGHT
    if full_h > ia_h:
        scale_factor = ia_h * 0.8 / full_h
        surface = scale(surface, (full_w * scale_factor, full_h * scale_factor))
    return surface


def _full_screen_flash(entities: EntityManager, alpha_start: int = 6, alpha_speed: int = 1):
    """Создать эффект полноэкранной вспышки"""
    gd = next(entities.get_by_class(GameData))
    gd.full_screen_flash_alpha = alpha_start
    gd.full_screen_flash_speed = alpha_speed


def _spark_splash(entities: EntityManager, animation_set: ComAnimationSet,
                  row: Optional[int] = None, col: Optional[int] = None, count: int = 15,
                  x: Optional[int] = None, y: Optional[int] = None):
    """Создать вспышку из искр на месте треугольника или на произвольной позиции"""
    if col or row:
        flip = _is_tri_oriented_down(row - GRID_HIDDEN_TOP_ROWS, col)
        x, y = _get_tri_center(row - GRID_HIDDEN_TOP_ROWS, col, flip)
    else:
        flip = False
    tri_h = SCREEN_HEIGHT_PX * GRID_TRI_HEIGHT
    tri_h_fx = tri_h * 0.2
    for i in range(count):
        r1 = randint(int(tri_h * 0.1), int(tri_h * 0.2))  # расстояние от центра
        r2 = r1 + randint(int(tri_h * 0.01), int(tri_h * 0.31))
        phi = randint(0, 359)
        start_x, start_y = polar2cart(r1, phi)
        end_x, end_y = polar2cart(r2, phi)
        animation_frame = randint(220, 255)
        animation_speed = randint(300, 500)
        move_time_sec = randint(10, 40) / 100
        entities.add(
            Spark(
                animation_set=animation_set,
                animation_looped=False,
                animation_frame=animation_frame,
                animation_frame_float=animation_frame + 0.0,
                animation_speed=animation_speed,
                x=start_x + x - SPARK_SIZE_PX / 2,
                y=start_y + y + (tri_h_fx * -1 if flip else 1) - SPARK_SIZE_PX / 2,
                speed_x=(end_x - start_x) / move_time_sec,
                speed_y=(end_y - start_y) / move_time_sec,
            )
        )


def _update_speed(gd: GameData, entities: EntityManager):
    """Перерасчет скорости игры"""
    old_speed = gd.speed
    gd.speed = next((i for i in range(len(SCORE_MAP)) if SCORE_MAP[i] >= gd.score), len(SCORE_MAP) - 1)
    if gd.speed != old_speed:
        # скорость игры увеличена
        SOUND_GAME_SPEED_UP.play()
        entities.add(
            TextSpeedPopup(
                surface=surface_text_speed_popup(gd.speed),
                x=FONT_SPEED_HEIGHT_PX / 2,
                y=int(SCREEN_HEIGHT_PX * INFO_AREA_HEIGHT) / 2 - FONT_SPEED_HEIGHT_PX / 1.95,
                speed_x=SCREEN_WIDTH_PX * GRID_TRI_WIDTH * 1.1,
                speed_y=0,
                live_until_time=monotonic() + 2,
            )
        )


def _event_score_update(gd: GameData, entities: EntityManager, animation_set: ComAnimationSet):
    """Проверка взятия активатора начисления очков"""
    if gd.event_score_coord:
        for row, col in MATRIX_ROW_COL:
            if gd.grid_figure_active[row, col] and \
                    row == gd.event_score_coord[0] and \
                    col == gd.event_score_coord[1]:
                # желтый треугольник взят
                SOUND_SCORE.play()
                _spark_splash(entities, animation_set, row, col)
                _full_screen_flash(entities)
                gd.event_score_coord = None
                gd.score += gd.event_score
                _update_speed(gd, entities)
                # popup
                tri_coord = _get_tri_coord(row - GRID_HIDDEN_TOP_ROWS, col, _is_tri_oriented_down(row, col))
                entities.add(
                    TextScorePopup(
                        surface=surface_text_score(f'+{gd.event_score}'),
                        x=tri_coord[0],
                        y=tri_coord[1] - FONT_SCORE_HEIGHT_PX * 0.9,
                        speed_x=0,
                        speed_y=-SCREEN_HEIGHT_PX * GRID_TRI_HEIGHT * 1.62,
                        live_until_time=monotonic() + 1.0,
                    )
                )
                break


def _event_no_intersect_update(gd: GameData, entities: EntityManager, animation_set: ComAnimationSet):
    """Проверка включения режима падения без препятствий"""
    if gd.event_no_intersect_coord:
        for row, col in MATRIX_ROW_COL:
            if gd.grid_figure_active[row, col] and \
                    row == gd.event_no_intersect_coord[0] and \
                    col == gd.event_no_intersect_coord[1]:
                # фиолетовый треугольник взят
                SOUND_EVENT_NO_INTERSECT.play()
                _spark_splash(entities, animation_set, row, col)
                _full_screen_flash(entities)
                gd.event_no_intersect_coord = None
                gd.event_no_intersect_now = True
                break


def _figure_active_to_static(gd: GameData):
    """Логика перехода активной фигуры в статику"""
    gd.grid_static = (gd.grid_static + gd.grid_figure_active).clip(min=0, max=1)
    gd.do_figure_spawn = True


def on_click_button_save_result(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    new_player_name = next(entities.get_by_class(InputPlayerName)).text.strip() or 'Player'
    gd = next(entities.get_by_class(GameData))
    SETTINGS_STORAGE.player_name = new_player_name
    SETTINGS_STORAGE.records_add(gd.score, new_player_name)
    gd.do_play = False


def on_click_button_resume_game(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    next(entities.get_by_class(GameData)).scene_active = FALL_SCENE_PLAY


def on_click_button_to_main_menu(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    next(entities.get_by_class(GameData)).do_play = False


def on_click_button_exit_game(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_BUTTON_CLICK.play()
    sleep(SOUND_BUTTON_CLICK.get_length())
    exit()


def on_edit_input_player_name(entities: EntityManager, pointer_pos: Vector2):  # noqa
    SOUND_TEXT_INPUT.play()


class SysInit(System):

    def __init__(self, entities: EntityManager):
        self.entities = entities

    def start(self):
        set_sound_volume(SETTINGS_STORAGE.sound)

        self.entities.init(
            Spark([], False, 0, 0, 0, 0, 0, 0, 0),
            TextScorePopup(surface=colored_block_surface(0, 1, 1), x=0, y=0, speed_x=0, speed_y=0, live_until_time=0),
            TextSpeedPopup(surface=colored_block_surface(0, 1, 1), x=0, y=0, speed_x=0, speed_y=0, live_until_time=0),
        )
        game_data = GameData(
            do_play=True,
            do_figure_fast_fall=False,
            do_figure_fast_fall_until=0.0,
            do_figure_spawn=True,
            do_figure_live_pause_until=0.0,
            scene_active=FALL_SCENE_PLAY,

            score=0,
            speed=0,
            pause_cnt=0,
            figure_dir=choice(PLUS_MINUS_ONE),
            figure_dir_last_change_time=0,
            figure_current=_get_random_figure_variant(),
            figure_next=_get_random_figure_variant(),
            figure_row=0,
            figure_col=0,
            last_move_time=0,

            event_score_coord=None,
            event_score=0,
            event_no_intersect_coord=None,
            event_no_intersect_now=False,

            grid_figure_active=m_create(row_cnt=MATRIX_ROWS, col_cnt=MATRIX_COLS),
            grid_static=m_create(row_cnt=MATRIX_ROWS, col_cnt=MATRIX_COLS),
            grid_temp1=m_create(row_cnt=MATRIX_ROWS, col_cnt=MATRIX_COLS),
            grid_temp2=m_create(row_cnt=MATRIX_ROWS, col_cnt=MATRIX_COLS),

            grid_rows_for_del=[],
            grid_cells_for_del=[],
            grid_cells_for_del_blocked=[],

            full_screen_flash_alpha=0,
            full_screen_flash_speed=255,
        )

        # для скринов
        # game_data.grid_static[MATRIX_ROWS - 2] = [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]
        # game_data.grid_static[MATRIX_ROWS - 1] = [1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0]
        # game_data.grid_static[MATRIX_ROWS - 4] = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # game_data.grid_static[MATRIX_ROWS - 3] = [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0]
        # game_data.grid_static[MATRIX_ROWS - 2] = [0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1]
        # game_data.grid_static[MATRIX_ROWS - 1] = [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1]

        # низ готовый к очистке
        # game_data.grid_static[MATRIX_ROWS - 2] = [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1]
        # game_data.grid_static[MATRIX_ROWS - 1] = [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1]

        # заблокированные треугольники
        # game_data.grid_static[MATRIX_ROWS -  1] = [1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1]
        # game_data.grid_static[MATRIX_ROWS -  2] = [1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1]
        # game_data.grid_static[MATRIX_ROWS -  3] = [1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1]
        # game_data.grid_static[MATRIX_ROWS -  4] = [1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1]

        _surface_border = surface_border()
        _border_h = _surface_border.get_height()

        _btn_w_scale = 2
        _btn_w = SCREEN_WIDTH_PX * BUTTON_WIDTH * _btn_w_scale
        _btn_h = gui_button_attrs(0, 0, '')['rect'].h
        _btn_x = SCREEN_WIDTH_PX / 2 - _btn_w / 2
        _btn_y = SCREEN_HEIGHT_PX * PLAY_AREA_HEIGHT * 0.38 + SCREEN_HEIGHT_PX * INFO_AREA_HEIGHT

        _text_linesize = FONT_TEXT_ML.get_linesize()
        _surface_text_game_results = surface_text_game_results(0)
        _surface_input_player_name = surface_input_player_name(IS_STATIC)
        _res_top = (SCREEN_HEIGHT_PX * 0.38 - _surface_text_game_results.get_height() / 2 -
                    SCREEN_HEIGHT_PX * INFO_AREA_HEIGHT)

        tri_coord21 = _get_tri_coord(2, 1, True)

        self.entities.add(
            game_data,
            InfoArea(
                surface_info_area(), x=0.0, y=0.0
            ),
            PlayArea(
                surface_play_area(), x=0.0, y=int(SCREEN_HEIGHT_PX * INFO_AREA_HEIGHT)
            ),
            Border(
                _surface_border, x=0.0, y=int(SCREEN_HEIGHT_PX * INFO_AREA_HEIGHT) - _border_h / 2
            ),

            TextStartGameGreetPopup(
                surface=surface_text_start_game_greet_popup(),
                x=tri_coord21[0],
                y=tri_coord21[1],
                speed_x=0,
                speed_y=SCREEN_HEIGHT_PX * GRID_TRI_HEIGHT * 0.62,
                live_until_time=monotonic() + 3.0,
            ),
            LabelPause(
                surface_label_pause(),
            ),
            LabelGameOver(
                surface_label_game_over(),
            ),
            Loading(
                surface_loading(), x=0.0, y=0.0,
            ),

            TextSpeed(
                colored_block_surface(0, 1, 1),
                x=FONT_SPEED_HEIGHT_PX / 2,
                y=int(SCREEN_HEIGHT_PX * INFO_AREA_HEIGHT) / 2 - FONT_SPEED_HEIGHT_PX / 1.95,
            ),
            TextScore(
                colored_block_surface(0, 1, 1),
                x=int(SCREEN_WIDTH_PX * 0.5) - FONT_SCORE_HEIGHT_PX / 4,
                y=int(SCREEN_HEIGHT_PX * INFO_AREA_HEIGHT) / 2 - FONT_SCORE_HEIGHT_PX / 1.9,
            ),
            TriangleActiveDown(surface_triangle_active_down()),
            TriangleActiveUp(surface_triangle_active_up()),
            TriangleGridDown(surface_triangle_grid_down()),
            TriangleGridUp(surface_triangle_grid_up()),
            TriangleStaticDown(surface_triangle_static_down()),
            TriangleStaticUp(surface_triangle_static_up()),

            TriangleScoreUp(surface_triangle_score_up()),
            TriangleScoreDown(surface_triangle_score_down()),
            TriangleScoreUpSmall(surface_triangle_score_up_small()),
            TriangleScoreDownSmall(surface_triangle_score_down_small()),
            TriangleNoIntersectUp(surface_triangle_no_intersect_up()),
            TriangleNoIntersectDown(surface_triangle_no_intersect_down()),

            DirectionArrowLeft(surface_direction_arrow_left()),
            DirectionArrowRight(surface_direction_arrow_right()),

            # Yellow White Fuchsia
            SparkDel1AnimationSet(tuple(
                surface_spark(
                    IMG_SPARK_LIGHT, 255 if i > 200 else i, '#FFFF00', '#FFFFFF', '#FF00FF') for i in range(256)
            )),
            # DeepPink Yellow Red
            SparkDel2AnimationSet(tuple(
                surface_spark(
                    IMG_SPARK_DARK, 255 if i > 200 else i, '#FF1493', '#FFFF00', '#FF0000') for i in range(256)
            )),

            FullScreenFlash(surface_full_screen_flash()),

            IconNextFigure(
                _surface_icon_next_figure(
                    game_data.figure_next,
                    colored_block_surface(0, 1, 1),
                    colored_block_surface(0, 1, 1)
                ),
            ),

            # gui
            ButtonResumeGame(
                scenes=[FALL_SCENE_PAUSE],
                on_click=on_click_button_resume_game,
                **gui_button_attrs(_btn_x, _btn_y + _btn_h * 2 * 1.61, I18N_FALL_RESUME_GAME, _btn_w_scale),
            ),
            ButtonToMainMenu(
                scenes=[FALL_SCENE_PAUSE],
                on_click=on_click_button_to_main_menu,
                **gui_button_attrs(_btn_x, _btn_y + _btn_h * 1 * 1.61, I18N_FALL_TO_MAIN_MENU, _btn_w_scale),
            ),
            ButtonExitGame(
                scenes=[FALL_SCENE_PAUSE],
                on_click=on_click_button_exit_game,
                **gui_button_attrs(_btn_x, _btn_y + _btn_h * 0 * 1.61, I18N_FALL_EXIT_GAME, _btn_w_scale),
            ),

            ButtonSaveResult(
                scenes=[FALL_SCENE_GAME_OVER],
                on_click=on_click_button_save_result,
                **gui_button_attrs(
                    _btn_x,
                    _res_top + _text_linesize * 7,
                    I18N_FALL_SAVE_RESULT,
                    _btn_w_scale
                ),
            ),
            TextGameResults(
                scenes=[FALL_SCENE_GAME_OVER],
                rect=(
                    SCREEN_WIDTH_PX / 2 - _surface_text_game_results.get_width() / 2,
                    _res_top,
                    *_surface_text_game_results.get_size()
                ),
                sf_text=_surface_text_game_results,
                sf_bg=colored_block_surface('#FFE4B599', *_surface_text_game_results.get_size()),
            ),
            InputPlayerName(
                scenes=[FALL_SCENE_GAME_OVER],
                rect=Rect(
                    SCREEN_WIDTH_PX / 2 - _surface_input_player_name.get_width() / 2,
                    _res_top + _text_linesize * 4,
                    *_surface_input_player_name.get_size()
                ),
                font=FONT_TEXT_ML,
                max_length=30,
                sf_static=_surface_input_player_name,
                sf_active=surface_input_player_name(IS_ACTIVE),
                mask=pygame.mask.from_surface(_surface_input_player_name),
                text=SETTINGS_STORAGE.player_name,
                cursor=0,
                on_confirm=on_click_button_save_result,
                on_edit=on_edit_input_player_name,
                state=IS_ACTIVE,
            ),
        )


class SysLiveFigure(System):

    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.spark_del1_animation_set = None
        self.spark_del2_animation_set = None
        self.gd: Optional[GameData] = None
        self._rows_for_del_found_now = False

    def start(self):
        self.spark_del1_animation_set = next(self.entities.get_by_class(SparkDel1AnimationSet))
        self.spark_del2_animation_set = next(self.entities.get_by_class(SparkDel2AnimationSet))
        self.gd = next(self.entities.get_by_class(GameData))

    def update(self):
        now_time = monotonic()

        # пауза
        if self.gd.scene_active == FALL_SCENE_PAUSE:
            return

        # конец игры
        if self.gd.scene_active == FALL_SCENE_GAME_OVER:
            return

        # пауза в логике игры
        if now_time - self.gd.do_figure_live_pause_until < 0:
            return

        # удаление заполненных строк, расчёт скорости (второй этап очистки строк, после паузы)
        if self.gd.grid_rows_for_del:
            pass  # todo CUT

        # скорость игры
        _fast_fall = self.gd.do_figure_fast_fall or self.gd.do_figure_fast_fall_until - now_time > 0
        if now_time - self.gd.last_move_time < (SPEED_FAST_FALL if _fast_fall else SPEED_MAP[self.gd.speed]):
            # фигуре еще не время двигаться
            return
        self.gd.last_move_time = now_time

        # отражение фигуры от стен
        if self.gd.figure_dir == -1 and any(self.gd.grid_figure_active[..., :1]) \
                or self.gd.figure_dir == 1 and any(self.gd.grid_figure_active[..., -1:]):
            pass  # todo CUT

        # создать расширенную матрицу для проверки на возможность падения по диагоналям:
        # добавляем: снизу для ориентированных вверх, справа и слева для ориентированных вниз
        pass  # todo CUT

        # создать матрицу следующей позиции фигуры
        self.gd.grid_temp2 = m_2d_move(self.gd.grid_figure_active, x=self.gd.figure_dir, y=-1)

        # продолжать ли падение фигуры
        if (not self.gd.event_no_intersect_now and m_intersects(self.gd.grid_temp2, self.gd.grid_static)) or \
                (not self.gd.event_no_intersect_now and m_intersects(self.gd.grid_temp1, self.gd.grid_static)) or \
                not m_is_sum_equals(self.gd.grid_temp2, self.gd.grid_figure_active):
            # фигура упала
            pass  # todo CUT
        else:
            # продолжить падение
            pass  # todo CUT

        # активаторы событий
        _event_score_update(self.gd, self.entities, self.spark_del1_animation_set)
        _event_no_intersect_update(self.gd, self.entities, self.spark_del1_animation_set)

        # создать новую фигуру (упала или не было)
        if self.gd.do_figure_spawn:
            pass  # todo CUT
            # проверка окончания игры
            if self.gd.grid_static[GRID_HIDDEN_TOP_ROWS - 1].sum():
                self.gd.scene_active = FALL_SCENE_GAME_OVER
                next(self.entities.get_by_class(TextGameResults)).sf_text = surface_text_game_results(self.gd.score)
                SOUND_GAME_OVER.play()
                return
            # генерация событий
            self.gd.event_score_coord = None
            self.gd.event_no_intersect_now = False
            self.gd.event_no_intersect_coord = None
            if randint(1, EVENT_SCORE_CHANCE) == 1:
                # EVENT_SCORE
                _event_score_coord = (randint(4, MATRIX_ROWS - 3), randint(0, MATRIX_COLS - 1))
                if not self.gd.grid_static[_event_score_coord[0], _event_score_coord[1]]:
                    self.gd.event_score_coord = _event_score_coord
                    self.gd.event_score = randint(*EVENT_SCORE_RANGE)
            elif randint(1, EVENT_SCORE_SMALL_CHANCE) == 1:
                # EVENT_SCORE_SMALL
                _event_score_coord = (randint(4, MATRIX_ROWS - 3), randint(0, MATRIX_COLS - 1))
                if not self.gd.grid_static[_event_score_coord[0], _event_score_coord[1]]:
                    self.gd.event_score_coord = _event_score_coord
                    self.gd.event_score = randint(*EVENT_SCORE_SMALL_RANGE)
            if randint(1, EVENT_NO_INTERSECT_CHANCE) == 1:
                # EVENT_NO_INTERSECT
                _event_no_intersect_coord = (randint(4, MATRIX_ROWS - 3), randint(0, MATRIX_COLS - 1))
                if not self.gd.grid_static[_event_no_intersect_coord[0], _event_no_intersect_coord[1]]:
                    self.gd.event_no_intersect_coord = _event_no_intersect_coord

        # поиск заполненных строк и заблокированных ячеек
        for row_pair in range(MATRIX_ROWS // 2):
            pass  # todo CUT

        if self._rows_for_del_found_now:
            # найдены строки для очистки (первый этап очистки строк, до паузы)

            # звук
            if not self.gd.grid_cells_for_del_blocked:
                SOUND_SCORE.play()
            SOUND_CLEAN_LINE.play()

            # расчёт очков
            cells_for_del = len(self.gd.grid_cells_for_del)
            if self.gd.grid_cells_for_del_blocked:
                # есть заблокированные треугольники
                self.gd.score += 0
                popup_text_score = '+0 :('
            elif cells_for_del == GRID_COLS * 2:
                # две строки заполнены полностью
                self.gd.score += cells_for_del * 2
                popup_text_score = f'+{cells_for_del}*2!!!'
            else:
                # одна строка заполнена полностью
                self.gd.score += cells_for_del
                popup_text_score = f'+{cells_for_del}'

            # popup за строки
            tri_coord = _get_tri_coord(
                self.gd.grid_rows_for_del[0] - GRID_HIDDEN_TOP_ROWS,
                7,
                _is_tri_oriented_down(self.gd.grid_rows_for_del[0], 7)
            )
            self.entities.add(
                TextScorePopup(
                    surface=surface_text_score(popup_text_score),
                    x=tri_coord[0],
                    y=tri_coord[1] - FONT_SCORE_HEIGHT_PX * 0.9,
                    speed_x=0,
                    speed_y=-SCREEN_HEIGHT_PX * GRID_TRI_HEIGHT * 1.62,
                    live_until_time=monotonic() + 1.0,
                )
            )

            # вспышка очистки
            for row, col in self.gd.grid_cells_for_del:
                _spark_splash(self.entities, self.spark_del1_animation_set, row, col,
                              1 if self.gd.grid_cells_for_del_blocked else 15)
            for row, col in self.gd.grid_cells_for_del_blocked:
                _spark_splash(self.entities, self.spark_del2_animation_set, row, col, 30)
            _full_screen_flash(self.entities, 12, 1)

            self._rows_for_del_found_now = False
            self.gd.do_figure_live_pause_until = now_time + SPEED_MAP[self.gd.speed]  # пауза момента очистки


class SysLive(System):

    def __init__(self, entities: EntityManager, clock: pygame.time.Clock):
        self.entities = entities
        self.clock = clock
        self.spark_del1_animation_set = None
        self.spark_del2_animation_set = None
        self.gd = None

    def start(self):
        self.spark_del1_animation_set = next(self.entities.get_by_class(SparkDel1AnimationSet))
        self.spark_del2_animation_set = next(self.entities.get_by_class(SparkDel2AnimationSet))
        self.gd = next(self.entities.get_by_class(GameData))

    def update(self):
        now_fps = self.clock.get_fps() or FPS_MAX
        now_time = monotonic()

        # пауза
        if self.gd.scene_active == FALL_SCENE_PAUSE:
            return

        # движение
        for speed_obj in self.entities.get_with_component(ComSpeed):
            speed_obj.x += speed_obj.speed_x / now_fps
            speed_obj.y += speed_obj.speed_y / now_fps

        # анимация
        for ani_obj in self.entities.get_with_component(ComAnimated):
            ani_obj.animation_frame_float -= ani_obj.animation_speed / now_fps
            ani_obj.animation_frame = ani_obj.animation_frame_float.__trunc__()  # быстрее int(), только для float
            if ani_obj.animation_frame_float < 0:
                if ani_obj.animation_looped:
                    ani_obj.animation_frame = len(ani_obj.animation_set.frames) - 1
                    ani_obj.animation_frame_float = float(ani_obj.animation_frame)
                else:
                    self.entities.delete_buffer_add(ani_obj)

        # ограничение по времени жизни
        for live_until_obj in self.entities.get_with_component(ComLiveTime):
            if live_until_obj.live_until_time < now_time:
                self.entities.delete_buffer_add(live_until_obj)

        self.entities.delete_buffer_purge()


class SysControl(System):

    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.event_getter: Callable[..., list[Event]] = pygame.event.get
        self.spark_del1_animation_set = None
        self.spark_del2_animation_set = None
        self.gd = None
        self._last_pointer_pos_down: Tuple[int, int] = (0, 0)  # запомненная позиция нажатия мыши или пальца
        self._last_pointer_pos_up: Tuple[int, int] = (0, 0)  # запомненная позиция отжатия мыши или пальца
        self._pointer_is_pressed = False  # указатель в состоянии нажатия
        self._pointer_action = None  # текущее событие указателя (мыши или пальца)
        self.mouse_event_set = (MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION)
        self.switch_dir_accuracy = SCREEN_WIDTH_PX * 0.03

    def start(self):
        self.spark_del1_animation_set = next(self.entities.get_by_class(SparkDel1AnimationSet))
        self.spark_del2_animation_set = next(self.entities.get_by_class(SparkDel2AnimationSet))
        self.gd = next(self.entities.get_by_class(GameData))
        self.switch_dir_accuracy = next(self.entities.get_by_class(TriangleActiveUp)).surface.get_width() * 0.38

    def update(self):
        for event in self.event_getter():
            event_type = event.type
            event_key = getattr(event, 'key', None)

            # получение событий указателя (мыши или пальца)
            self._pointer_action = None
            if event_type == MOUSEBUTTONDOWN:
                # тест вспышки
                # _spark_splash(self.entities, self.spark_del2_animation_set, 3, 3)
                # _spark_splash(self.entities, self.spark_del1_animation_set, 3, 8)
                # for i in range(15):
                #     _spark_splash(self.entities, self.spark_del1_animation_set, 5, i)
                # _full_screen_flash(self.entities, 12, 1)
                # кнопка мыши нажата
                self._last_pointer_pos_down = event.pos
                self._pointer_is_pressed = True
            if event_type == MOUSEBUTTONUP:
                # кнопка мыши отпущена
                self._last_pointer_pos_up = event.pos
                self._pointer_is_pressed = False
                dx = self._last_pointer_pos_up[0] - self._last_pointer_pos_down[0]
                dy = self._last_pointer_pos_up[1] - self._last_pointer_pos_down[1]
                if abs(dx) < self.switch_dir_accuracy and abs(dy) < self.switch_dir_accuracy:
                    self._pointer_action = PA_SWITCH_DIR
                elif abs(dy) > abs(dx):
                    self._pointer_action = PA_ROTATE if dy < 0 else PA_MOVE_FAST
                else:
                    self._pointer_action = PA_MOVE_LEFT if dx < 0 else PA_MOVE_RIGHT

            # gui
            if self.gd.scene_active != FALL_SCENE_PLAY:
                if control_button(event, event_type, self.gd.scene_active, self.entities):
                    continue
                control_input_activate(event, event_type, self.gd.scene_active, self.entities)
                control_input_edit(event, event_type, event_key, self.gd.scene_active, self.entities)

            # выйти из игры
            if event_type == QUIT:
                exit()

            # конец игры
            if self.gd.scene_active == FALL_SCENE_GAME_OVER:
                continue  # *не return

            # пауза
            if event_type == KEYDOWN and event_key in (K_SPACE, K_AC_BACK, K_ESCAPE) or \
                    event_type == MOUSEBUTTONUP and event.pos[1] <= SCREEN_HEIGHT_PX * INFO_AREA_HEIGHT:
                if self.gd.scene_active == FALL_SCENE_PAUSE:
                    self.gd.scene_active = FALL_SCENE_PLAY
                    continue
                else:
                    self.gd.scene_active = FALL_SCENE_PAUSE
                    self.gd.pause_cnt += 1
                    SOUND_PAUSE.play()

            # выкл управление при паузе
            if self.gd.scene_active == FALL_SCENE_PAUSE:
                continue  # *не return

            # сдвинуть влево или вправо
            if event_type == KEYDOWN and event_key in (K_RIGHT, K_LEFT) or \
                    self._pointer_action in (PA_MOVE_LEFT, PA_MOVE_RIGHT):
                pass  # todo CUT

            # повернуть
            if event_type == KEYDOWN and event_key == K_UP or self._pointer_action == PA_ROTATE:
                pass  # todo CUT

            # вкл ускоренное падение (кнопки)
            if event_type == KEYDOWN and event_key == K_DOWN:
                self.gd.do_figure_fast_fall = True
                SOUND_FAST_FALL.play()

            # выкл ускоренное падение (кнопки)
            if event_type == KEYUP and event_key == K_DOWN:
                self.gd.do_figure_fast_fall = False

            # вкл ускоренное падение на время (тач и мышь)
            if self._pointer_action == PA_MOVE_FAST:
                self.gd.do_figure_fast_fall_until = monotonic() + SPEED_FAST_FALL * SPEED_FAST_FALL_CNT
                SOUND_FAST_FALL.play()

            # изменить направление падения
            if event_type == KEYDOWN and event_key in (K_SPACE, K_LSHIFT, K_RSHIFT) or \
                    self._pointer_action == PA_SWITCH_DIR:
                self.gd.figure_dir = self.gd.figure_dir * -1
                self.gd.figure_dir_last_change_time = monotonic()
                SOUND_CHANGE_DIR.play()


class SysDraw(System):

    def __init__(self, entities: EntityManager, display: Surface):
        self.entities = entities
        self.display = display

        self.tri_active_up = None
        self.tri_active_down = None
        self.tri_grid_up = None
        self.tri_grid_down = None
        self.tri_static_up = None
        self.tri_static_down = None
        self.tri_score_up = None
        self.tri_score_down = None
        self.tri_score_up_small = None
        self.tri_score_down_small = None
        self.tri_no_intersect_up = None
        self.tri_no_intersect_down = None
        self.direction_arrow_left = None
        self.direction_arrow_right = None
        self.spark_del1_animation_set = None
        self.spark_del2_animation_set = None
        self.label_pause = None
        self.label_game_over = None
        self.full_screen_flash = None
        self.gd: Optional[GameData] = None
        self._score_cache = -1
        self._speed_cache = -1
        self._figure_next_cache = (-1, -1)
        self._icon_next_figure_w_cache = 0
        self._icon_next_figure_h_cache = 0
        self._static_surface = colored_block_surface(0, SCREEN_WIDTH_PX, SCREEN_HEIGHT_PX)

    def start(self):
        self.tri_active_up = next(self.entities.get_by_class(TriangleActiveUp))
        self.tri_active_down = next(self.entities.get_by_class(TriangleActiveDown))
        self.tri_grid_up = next(self.entities.get_by_class(TriangleGridUp))
        self.tri_grid_down = next(self.entities.get_by_class(TriangleGridDown))
        self.tri_static_up = next(self.entities.get_by_class(TriangleStaticUp))
        self.tri_static_down = next(self.entities.get_by_class(TriangleStaticDown))
        self.tri_score_up = next(self.entities.get_by_class(TriangleScoreUp))
        self.tri_score_down = next(self.entities.get_by_class(TriangleScoreDown))
        self.tri_score_up_small = next(self.entities.get_by_class(TriangleScoreUpSmall))
        self.tri_score_down_small = next(self.entities.get_by_class(TriangleScoreDownSmall))
        self.tri_no_intersect_up = next(self.entities.get_by_class(TriangleNoIntersectUp))
        self.tri_no_intersect_down = next(self.entities.get_by_class(TriangleNoIntersectDown))
        self.direction_arrow_left = next(self.entities.get_by_class(DirectionArrowLeft))
        self.direction_arrow_right = next(self.entities.get_by_class(DirectionArrowRight))
        self.spark_del1_animation_set = next(self.entities.get_by_class(SparkDel1AnimationSet))
        self.spark_del2_animation_set = next(self.entities.get_by_class(SparkDel2AnimationSet))
        self.label_pause = next(self.entities.get_by_class(LabelPause))
        self.label_game_over = next(self.entities.get_by_class(LabelGameOver))
        self.full_screen_flash = next(self.entities.get_by_class(FullScreenFlash))
        self.gd = next(self.entities.get_by_class(GameData))
        # Поле информации об игре и Игровое поле
        for visible_entity in self.entities.get_by_class(PlayArea, InfoArea, Border):
            self._static_surface.blit(visible_entity.surface, (visible_entity.x, visible_entity.y))
        # сетка треугольников
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                flip = _is_tri_oriented_down(row, col)
                tri_coord = _get_tri_coord(row, col, flip)
                self._static_surface.blit(
                    self.tri_grid_down.surface if flip else self.tri_grid_up.surface,
                    tri_coord
                )

    def update(self):
        now_time = monotonic()

        if not self.gd.do_play:
            # игра не готова к отрисовке
            loading_sf = next(self.entities.get_by_class(Loading))
            self.display.blit(loading_sf.surface, (loading_sf.x, loading_sf.y))
            return

        # обновление поверхности следующей фигуры
        if self._figure_next_cache != self.gd.figure_next:
            self._figure_next_cache = self.gd.figure_next
            new_surface = _surface_icon_next_figure(
                self.gd.figure_next, self.tri_active_up.surface, self.tri_active_down.surface)
            next(self.entities.get_by_class(IconNextFigure)).surface = new_surface
            self._icon_next_figure_w_cache, self._icon_next_figure_h_cache = new_surface.get_size()

        # обновление поверхности динамических цифр
        if self._score_cache != self.gd.score:
            self._score_cache = self.gd.score
            text_score = next(self.entities.get_by_class(TextScore))
            if self.gd.speed >= 5 and PACKAGE_EDITION == PACKAGE_EDITION_FREE:
                text = 'free'
            else:
                text = self.gd.score
            text_score.surface = surface_text_score(text)
            text_score.x = SCREEN_WIDTH_PX * INFO_AREA_WIDTH / 2 - text_score.surface.get_size()[0] / 2
        if self._speed_cache != self.gd.speed:
            self._speed_cache = self.gd.speed
            next(self.entities.get_by_class(TextSpeed)).surface = surface_text_speed(self.gd.speed)

        # статика
        self.display.blit(self._static_surface, (0, 0))

        # треугольники
        draw_figure_dir_arrow = now_time - self.gd.figure_dir_last_change_time < 0.2
        if draw_figure_dir_arrow:
            dir_arr_alpha = int(
                DIR_ARROW_ALPHA - DIR_ARROW_ALPHA * (now_time - self.gd.figure_dir_last_change_time) * 5)
            self.direction_arrow_right.surface.set_alpha(dir_arr_alpha)
            self.direction_arrow_left.surface.set_alpha(dir_arr_alpha)
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                flip = _is_tri_oriented_down(row, col)
                tri_coord = _get_tri_coord(row, col, flip)
                # статичные
                if self.gd.grid_static[row + GRID_HIDDEN_TOP_ROWS, col]:
                    temp_coord = (row + GRID_HIDDEN_TOP_ROWS, col)
                    if temp_coord not in self.gd.grid_cells_for_del and \
                            temp_coord not in self.gd.grid_cells_for_del_blocked:
                        self.display.blit(
                            self.tri_static_down.surface if flip else self.tri_static_up.surface,
                            tri_coord
                        )
                # фигура
                if self.gd.grid_figure_active[row + GRID_HIDDEN_TOP_ROWS, col]:
                    if self.gd.event_no_intersect_now:
                        # проходящая через препятствия
                        self.display.blit(
                            self.tri_no_intersect_down.surface if flip else self.tri_no_intersect_up.surface,
                            tri_coord
                        )
                    else:
                        # обычная
                        self.display.blit(
                            self.tri_active_down.surface if flip else self.tri_active_up.surface,
                            tri_coord
                        )
                    # стрелка направления движения фигуры
                    if draw_figure_dir_arrow:
                        self.display.blit(
                            self.direction_arrow_right.surface
                            if self.gd.figure_dir == 1 else self.direction_arrow_left.surface,
                            _get_figure_dir_coord(row, col, flip)
                        )

        # индикатор следующей фигуры
        self.display.blit(
            next(self.entities.get_by_class(IconNextFigure)).surface,
            (
                SCREEN_WIDTH_PX * INFO_AREA_WIDTH - self._icon_next_figure_w_cache - FONT_SPEED_HEIGHT_PX / 2,
                SCREEN_HEIGHT_PX * INFO_AREA_HEIGHT / 2 - self._icon_next_figure_h_cache / 2
            )
        )

        # активатор получения очков
        if self.gd.event_score_coord:
            flip = _is_tri_oriented_down(*self.gd.event_score_coord)
            temp_coord = self.gd.event_score_coord[0] - GRID_HIDDEN_TOP_ROWS, self.gd.event_score_coord[1]
            if self.gd.event_score > EVENT_SCORE_SMALL_RANGE[1]:
                score_surface = self.tri_score_down.surface if flip else self.tri_score_up.surface
            else:
                score_surface = self.tri_score_down_small.surface if flip else self.tri_score_up_small.surface
            self.display.blit(score_surface, _get_tri_coord(*temp_coord, flip))

        # активатор режима падения без препятствий
        if self.gd.event_no_intersect_coord:
            flip = _is_tri_oriented_down(*self.gd.event_no_intersect_coord)
            temp_coord = self.gd.event_no_intersect_coord[0] - GRID_HIDDEN_TOP_ROWS, self.gd.event_no_intersect_coord[1]
            self.display.blit(
                self.tri_no_intersect_down.surface if flip else self.tri_no_intersect_up.surface,
                _get_tri_coord(*temp_coord, flip)
            )

        # искры
        for spark in self.entities.get_by_class(Spark):
            self.display.blit(spark.animation_set.frames[spark.animation_frame], (spark.x, spark.y))

        # текст: очки и скорость, приветствие
        for visible_entity in self.entities.get_by_class(
                TextScore, TextSpeed, TextScorePopup, TextSpeedPopup, TextStartGameGreetPopup):
            self.display.blit(visible_entity.surface, (visible_entity.x, visible_entity.y))

        # полноэкранная вспышка
        if self.gd.full_screen_flash_alpha > 0:
            self.full_screen_flash.surface.set_alpha(self.gd.full_screen_flash_alpha)
            self.display.blit(self.full_screen_flash.surface, (0, 0))
            self.gd.full_screen_flash_alpha -= self.gd.full_screen_flash_speed

        # пауза - текст
        if self.gd.scene_active == FALL_SCENE_PAUSE:
            label_w, label_h = self.label_pause.surface.get_size()
            self.display.blit(
                self.label_pause.surface,
                (
                    SCREEN_WIDTH_PX * PLAY_AREA_WIDTH * 0.5 - label_w / 2,
                    SCREEN_HEIGHT_PX * PLAY_AREA_HEIGHT * 0.38 - label_h / 2 - SCREEN_HEIGHT_PX * INFO_AREA_HEIGHT
                )
            )

        # конец игры - текст
        if self.gd.scene_active == FALL_SCENE_GAME_OVER:
            label_w, label_h = self.label_game_over.surface.get_size()
            self.display.blit(
                self.label_game_over.surface,
                (
                    SCREEN_WIDTH_PX * PLAY_AREA_WIDTH * 0.5 - label_w / 2,
                    SCREEN_HEIGHT_PX * 0.8 - label_h / 2 - SCREEN_HEIGHT_PX * INFO_AREA_HEIGHT
                )
            )

        # gui
        if self.gd.scene_active != FALL_SCENE_PLAY:
            draw_text_ml(self.display, self.gd.scene_active, self.entities)
            draw_button(self.display, self.gd.scene_active, self.entities)
            draw_input(self.display, self.gd.scene_active, self.entities)
