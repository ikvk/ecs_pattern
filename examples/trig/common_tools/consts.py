import warnings

import pygame
from pygame import SRCALPHA

try:
    from common_tools.build_flags import PACKAGE_EDITION  # устанавливается скриптом при сборке
except (ModuleNotFoundError, ImportError):
    warnings.warn('Create common_tools/build_flags.py with PACKAGE_EDITION str var')
    PACKAGE_EDITION = 'free'
from common_tools.compatibility import is_android, get_user_data_dir
from common_tools.settings import SettingsStorage, SETTING_GRAPHIC_LOW, SETTING_GRAPHIC_MIDDLE, SETTING_GRAPHIC_HIGH, \
    SETTING_SCREEN_MODE_FULL, SETTING_SOUND_NORMAL, SETTING_SOUND_QUIET, SETTING_SOUND_DISABLED

pygame.mixer.pre_init(44100, -16, 2, 512)  # best place - before calling the top level pygame.init()
pygame.init()  # init all imported pygame modules

# общие
PLUS_MINUS_ONE = (-1, 1)

# ДУБЛИРУЮЩИЕСЯ в build_apk.sh !
PACKAGE_NAME = f'game.ikvk.trig_fall_{PACKAGE_EDITION}'
GAME_NAME = 'Trig fall'
GAME_VERSION = f'1.0.3 {PACKAGE_EDITION}'

# варианты игры, лучше проверять на PACKAGE_EDITION_FREE
PACKAGE_EDITION_PAY = 'pay'
PACKAGE_EDITION_PAY_HUAWEI = 'pay.hw'
PACKAGE_EDITION_FREE = 'free'

# хранилище настроек
SETTINGS_STORAGE = SettingsStorage(get_user_data_dir(PACKAGE_NAME), is_android())

# Рабочий стол
# Длина списка get_desktop_sizes отличается от количества подключенных мониторов,
# поскольку рабочий стол может быть зеркально отображен на нескольких мониторах.
# Размеры рабочего стола указывают не на максимальное разрешение монитора,
# поддерживаемое оборудованием, а на размер рабочего стола, настроенный в операционной системе.
_desktop_size_set = pygame.display.get_desktop_sizes()  # рабочие столы
_desktop_max_h = max(height for width, height in _desktop_size_set)  # максимальная высота среди рабочих столов
_desktop_w, _desktop_h = next((w, h) for w, h in _desktop_size_set if h == _desktop_max_h)  # выбранный рабочий стол
_is_horizontal_desktop = _desktop_h < _desktop_w

# зависимость размеров от ориентации экрана
if _is_horizontal_desktop:
    _desktop_w = _desktop_h * 0.62
    _desktop_h = _desktop_h

# качество графики
_quality_div = {SETTING_GRAPHIC_LOW: 3, SETTING_GRAPHIC_MIDDLE: 2, SETTING_GRAPHIC_HIGH: 1}[SETTINGS_STORAGE.graphic]
_desktop_w = _desktop_w / _quality_div
_desktop_h = _desktop_h / _quality_div

# зависимость размеров от режима экрана
if SETTINGS_STORAGE.screen_mode == SETTING_SCREEN_MODE_FULL:
    SCREEN_WIDTH = _desktop_w  # ширина области для рендера в пикселях
    SCREEN_HEIGHT = _desktop_h  # высота области для рендера в пикселях
else:  # SETTING_SCREEN_MODE_WINDOW
    SCREEN_HEIGHT = int(_desktop_h / 100) * 100 - 100
    SCREEN_WIDTH = SCREEN_HEIGHT * 0.62

# рендер
FPS_MAX = 30
FPS_SHOW = True if SETTINGS_STORAGE.player_name.endswith('@') else False  # отображать FPS
SPARK_SIZE_PX = SCREEN_HEIGHT // 132
SURFACE_ARGS = dict(flags=SRCALPHA, depth=32)

# шрифт
FONT_COLOR_SPEED1 = '#4682B4'
FONT_COLOR_SPEED2 = '#FFE4B5'
FONT_COLOR_SCORE1 = '#FFD700'
FONT_COLOR_SCORE2 = '#8B4513'
FONT_COLOR_PAUSE1 = '#4682B4'
FONT_COLOR_PAUSE2 = '#8B4513'
FONT_COLOR_GAME_OVER1 = '#B22222'
FONT_COLOR_GAME_OVER2 = '#ffcc7a'

# Размер видимого игрового поля
GRID_ROWS = 18
GRID_COLS = 17
GRID_HIDDEN_TOP_ROWS = 2
assert GRID_ROWS % 2 == 0  # *очистка заполненных строк делается на пару строк

# размеры видимых игровых сущностей (коэффициенты от ширины и высоты экрана)
INFO_AREA_WIDTH = 1.0
INFO_AREA_HEIGHT = 0.07
PLAY_AREA_WIDTH = 1.0
PLAY_AREA_HEIGHT = 1.0 - INFO_AREA_HEIGHT
_pah = SCREEN_HEIGHT * PLAY_AREA_HEIGHT
_paw = SCREEN_WIDTH * PLAY_AREA_WIDTH
PLAY_AREA_PADDING = 0.033  # поля игрового поля
PLAY_AREA_H_W_RATIO = _pah / _paw  # соотношение игровой области: высота / ширина
GRID_H_W_RATIO = 1.55  # требуемое соотношение: высота / ширина
GRID_MARGIN_VER = 0.0  # отступ сверху и снизу
GRID_MARGIN_HOR = 0.0  # отступ справа и слева
_grid_margin = (_pah - _paw * GRID_H_W_RATIO) / 2
if PLAY_AREA_H_W_RATIO > GRID_H_W_RATIO:
    GRID_MARGIN_VER = abs(_grid_margin) / SCREEN_HEIGHT
else:
    GRID_MARGIN_HOR = abs(_grid_margin) / SCREEN_WIDTH
GRID_WIDTH = PLAY_AREA_WIDTH - PLAY_AREA_PADDING * 2 - GRID_MARGIN_HOR * 2
GRID_HEIGHT = PLAY_AREA_HEIGHT - PLAY_AREA_PADDING * 2 - GRID_MARGIN_VER * 2
GRID_TRI_WIDTH = GRID_WIDTH / GRID_COLS * 0.81 * 2
GRID_TRI_HEIGHT = GRID_HEIGHT / GRID_ROWS * 0.855
GRID_TRI_GAP_COL = GRID_WIDTH / GRID_COLS * 0.18
GRID_TRI_GAP_ROW = GRID_HEIGHT / GRID_ROWS * 0.17
GRID_TRI_Y_CORR = 0.0015  # коррекция в зависимости от направления вершины вверх или вниз

# игра
SPEED_LEVEL_COUNT = 31  # количество уровней скорости
SPEED_MAP = tuple(0.95 - 0.61 / SPEED_LEVEL_COUNT * i for i in range(SPEED_LEVEL_COUNT))  # скорость уровней игры, сек
SCORE_MAP = tuple(int(100 * i) for i in range(SPEED_LEVEL_COUNT))  # уровни очков для переключения скорости
SPEED_FAST_FALL = 0.1  # скорость падения фигуры с включенным ускорением, сек
SPEED_FAST_FALL_CNT = 3 if PACKAGE_EDITION == PACKAGE_EDITION_FREE else 4  # N строк - для тачей
EVENT_SCORE_CHANCE = 15 if PACKAGE_EDITION == PACKAGE_EDITION_FREE else 10  # выпадать 1 раз за N фигур
EVENT_NO_INTERSECT_CHANCE = 18  # выпадать 1 раз за N фигур

# размеры сущностей меню (коэффициенты от ширины и высоты экрана)
MENU_ROOT_AREA_GAME_NAME_HEIGHT = 0.38  # часть главного экрана для имени игры
MENU_ROOT_AREA_BUTTONS_HEIGHT = 1 - MENU_ROOT_AREA_GAME_NAME_HEIGHT  # часть главного экрана для кнопок
MENU_ROOT_BUTTON_GROUP_WIDTH = 0.95  # ширина группы кнопок главного меню
MENU_ROOT_BUTTON_GROUP_GAP_WIDTH = 0.03  # отступ между кнопками группы кнопок главного меню
MENU_SHINE_WIDTH = 0.38  # *сияние квадратное

# базовые уровни громкости
SOUND_LEVEL = {
    SETTING_SOUND_NORMAL: 0.61,
    SETTING_SOUND_QUIET: 0.23,
    SETTING_SOUND_DISABLED: 0,
}

# gui
TEXT_ML_WIDTH = 0.95  # размер блока для многострочных текстов
TEXT_ML_HEIGHT = 0.95  # размер блока для многострочных текстов
BUTTON_WIDTH = 0.28  # базовая ширина прямоугольных кнопок

# сцены меню
MENU_SCENE_ROOT = 1
MENU_SCENE_ABOUT = 2
MENU_SCENE_GUIDE = 3
MENU_SCENE_RECORDS = 4
MENU_SCENE_SETTINGS = 5

# сцены меню
FALL_SCENE_PLAY = 1
FALL_SCENE_PAUSE = 2
FALL_SCENE_GAME_OVER = 3

# размеры матриц с данными
MATRIX_ROWS = GRID_ROWS + GRID_HIDDEN_TOP_ROWS
MATRIX_COLS = GRID_COLS
MATRIX_ROW_COL = tuple((row, col) for row in range(MATRIX_ROWS) for col in range(MATRIX_COLS))

# События указателя мыши или пальца, Pointer Action
PA_MOVE_LEFT = 1
PA_MOVE_RIGHT = 2
PA_ROTATE = 3
PA_SWITCH_DIR = 4
PA_MOVE_FAST = 5
PA_NAMES = {
    PA_MOVE_LEFT: 'MOVE_LEFT',
    PA_MOVE_RIGHT: 'MOVE_RIGHT',
    PA_ROTATE: 'ROTATE',
    PA_SWITCH_DIR: 'SWITCH_DIR',
    PA_MOVE_FAST: 'MOVE_FAST',
}

# Cостояния кнопок, Button States
BS_STATIC = 1
BS_HOVER = 2
BS_PRESSED = 3
BS_NAMES = {
    BS_STATIC: 'STATIC',
    BS_HOVER: 'HOVER',
    BS_PRESSED: 'PRESSED',
}

# Cостояния полей ввода, Input States
IS_STATIC = 1
IS_ACTIVE = 2
IS_NAMES = {
    IS_STATIC: 'STATIC',
    IS_ACTIVE: 'ACTIVE',
}

# Фигуры
FIGURE_COLS = 5
FIGURE_ROWS = 3
FIGURE_CENTER_PAD = GRID_COLS // 2 - FIGURE_COLS // 2 + 2  # постоянный отступ колонок при создании
assert FIGURE_CENTER_PAD % 2 == 0
FIGURE_ROW_COL = tuple((row, col) for row in range(FIGURE_ROWS) for col in range(FIGURE_COLS))
FIGURES = (  # Все варианты фигур, верхний левый угол фигуры - треугольник с вершиной вверху
    # single 1
    (
        (
            (1, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
        ),
        (
            (0, 1, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
        ),
    ),
    # single 1 copy
    # (
    #     (
    #         (1, 0, 0, 0, 0),
    #         (0, 0, 0, 0, 0),
    #         (0, 0, 0, 0, 0),
    #     ),
    #     (
    #         (0, 1, 0, 0, 0),
    #         (0, 0, 0, 0, 0),
    #         (0, 0, 0, 0, 0),
    #     ),
    # ),
    # double 1
    (
        (
            (1, 0, 0, 0, 0),
            (1, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
        ),
        (
            (0, 1, 1, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
        ),
        (
            (0, 0, 0, 0, 0),
            (0, 1, 1, 0, 0),
            (0, 0, 0, 0, 0),
        ),
    ),
    # triple 1
    (
        (
            (1, 1, 1, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
        ),
        (
            (0, 0, 1, 0, 0),
            (0, 1, 1, 0, 0),
            (0, 0, 0, 0, 0),
        ),
        (
            (1, 0, 0, 0, 0),
            (1, 1, 0, 0, 0),
            (0, 0, 0, 0, 0),
        ),
    ),
    # triple 2
    (
        (
            (1, 1, 0, 0, 0),
            (1, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
        ),
        (
            (0, 1, 1, 0, 0),
            (0, 0, 1, 0, 0),
            (0, 0, 0, 0, 0),
        ),
        (
            (0, 0, 0, 0, 0),
            (1, 1, 1, 0, 0),
            (0, 0, 0, 0, 0),
        ),
    ),
    # triple 3
    (
        (
            (0, 1, 1, 1, 0),
            (0, 0, 1, 0, 0),
            (0, 0, 0, 0, 0),
        ),
        (
            (0, 0, 1, 0, 0),
            (0, 1, 1, 1, 0),
            (0, 0, 0, 0, 0),
        ),
    ),
    # quadruple 1
    (
        (
            (0, 0, 1, 0, 0),
            (0, 1, 1, 0, 0),
            (0, 1, 0, 0, 0),
        ),
        (
            (0, 1, 1, 0, 0),
            (0, 0, 1, 1, 0),
            (0, 0, 0, 0, 0),
        ),
        (
            (0, 0, 0, 0, 0),
            (0, 1, 1, 1, 1),
            (0, 0, 0, 0, 0),
        ),
    ),
    # quadruple 2
    (
        (
            (0, 0, 0, 0, 0),
            (1, 1, 1, 1, 0),
            (0, 0, 0, 0, 0),
        ),
        (
            (0, 0, 1, 1, 0),
            (0, 1, 1, 0, 0),
            (0, 0, 0, 0, 0),
        ),
        (
            (0, 0, 1, 0, 0),
            (0, 0, 1, 1, 0),
            (0, 0, 0, 1, 0),
        ),
    ),
    # quadruple 3
    (
        (
            (1, 1, 1, 0, 0),
            (1, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
        ),
        (
            (1, 1, 1, 0, 0),
            (0, 0, 1, 0, 0),
            (0, 0, 0, 0, 0),
        ),
        (
            (0, 1, 1, 0, 0),
            (0, 1, 1, 0, 0),
            (0, 0, 0, 0, 0),
        ),
        (
            (0, 0, 1, 0, 0),
            (1, 1, 1, 0, 0),
            (0, 0, 0, 0, 0),
        ),
        (
            (1, 0, 0, 0, 0),
            (1, 1, 1, 0, 0),
            (0, 0, 0, 0, 0),
        ),
        (
            (1, 1, 0, 0, 0),
            (1, 1, 0, 0, 0),
            (0, 0, 0, 0, 0),
        ),
    ),
)

for figure in FIGURES:
    for variant in figure:
        if len(variant) != FIGURE_ROWS:
            raise ValueError(f'Wrong figure ROWS config: {variant}')
        for row in variant:
            if len(row) != FIGURE_COLS:
                raise ValueError(f'Wrong figure COLS config: {row}')
