import pygame
from pygame import SRCALPHA

pygame.init()  # init all imported pygame modules

# Рабочий стол
# Длина списка get_desktop_sizes отличается от количества подключенных мониторов,
# поскольку рабочий стол может быть зеркально отображен на нескольких мониторах.
# Размеры рабочего стола указывают не на максимальное разрешение монитора,
# поддерживаемое оборудованием, а на размер рабочего стола, настроенный в операционной системе.
_desktop_size_set = pygame.display.get_desktop_sizes()  # рабочие столы
_desktop_max_h = max(height for width, height in _desktop_size_set)  # максимальная высота среди рабочих столов
_desktop_w, _desktop_h = next((w, h) for w, h in _desktop_size_set if h == _desktop_max_h)  # выбранный рабочий стол
_is_horizontal_desktop = _desktop_h < _desktop_w

# качество графики
_quality_div = 1  # {SETTING_GRAPHIC_LOW: 3, SETTING_GRAPHIC_MIDDLE: 2, SETTING_GRAPHIC_HIGH: 1}
_desktop_w = _desktop_w / _quality_div
_desktop_h = _desktop_h / _quality_div

# зависимость размеров от режима экрана
SETTING_SCREEN_IS_FULLSCREEN = False
if SETTING_SCREEN_IS_FULLSCREEN:
    SCREEN_WIDTH = _desktop_w  # ширина области для рендера в пикселях
    SCREEN_HEIGHT = _desktop_h  # высота области для рендера в пикселях
else:  # WINDOW
    SCREEN_HEIGHT = _desktop_h * 0.8
    SCREEN_WIDTH = SCREEN_HEIGHT

# сцена 1
SHINE_SIZE = 0.38  # от высоты
SHINE_WARM_SPEED_MUL = 10  # от высоты
SNOWFLAKE_SIZE_FROM = 0.002  # от высоты
SNOWFLAKE_SIZE_TO = 0.03  # от высоты
SNOWFLAKE_SIZE_CNT = 64
SNOWFLAKE_SIZE_STEP = (SNOWFLAKE_SIZE_TO - SNOWFLAKE_SIZE_FROM) / SNOWFLAKE_SIZE_CNT
SNOWFLAKE_CNT = 10_000
SNOWFLAKE_ANIMATION_FRAMES = 360  # кадров в полном обороте
SNOWFLAKE_ANIMATION_SPEED_MIN = 2.0  # fps
SNOWFLAKE_ANIMATION_SPEED_MAX = 40.0  # fps
SNOWFLAKE_SPEED_X_RANGE = (-10.0, 10.0)
SNOWFLAKE_SPEED_Y_RANGE = (15.0, 40.0)

# рендер
FPS_MAX = 60
FPS_SHOW = True
SURFACE_ARGS = dict(flags=SRCALPHA, depth=32)
