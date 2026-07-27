import pygame
from pygame import SRCALPHA

pygame.mixer.pre_init(44100, -16, 2, 512)  # best place - before calling the top level pygame.init()
pygame.init()  # init all imported pygame modules

# Рабочий стол
# Длина списка get_desktop_sizes отличается от количества подключенных мониторов,
# поскольку рабочий стол может быть зеркально отображен на нескольких мониторах.
# Размеры рабочего стола указывают не на максимальное разрешение монитора,
# поддерживаемое оборудованием, а на размер рабочего стола, настроенный в операционной системе.
_desktop_size_set = pygame.display.get_desktop_sizes()  # рабочие столы
_desktop_max_h = max(height for width, height in _desktop_size_set)  # максимальная высота среди рабочих столов
_desktop_w, _desktop_h = next((w, h) for w, h in _desktop_size_set if h == _desktop_max_h)  # выбранный рабочий стол
_is_vertical_desktop = _desktop_h > _desktop_w

# зависимость размеров от ориентации экрана
if _is_vertical_desktop:
    _desktop_h = _desktop_w * 0.62
    _desktop_w = _desktop_w

# зависимость размеров от режима экрана
window_mode = True
if window_mode:
    # режим в окне
    SCREEN_WIDTH_PX = _desktop_w * 0.8
    SCREEN_HEIGHT_PX = SCREEN_WIDTH_PX * 0.62
else:
    # полноэкранный режим
    SCREEN_WIDTH_PX = _desktop_w  # ширина области для рендера в пикселях
    SCREEN_HEIGHT_PX = _desktop_h  # высота области для рендера в пикселях

# размер экрана - int
SCREEN_WIDTH_PX = int(SCREEN_WIDTH_PX)
SCREEN_HEIGHT_PX = int(SCREEN_HEIGHT_PX)

# рендер
FPS_MAX = 60
FPS_SHOW = False  # отображать FPS
DUST_SIZE_PX = SCREEN_HEIGHT_PX * 0.06
SURFACE_ARGS = dict(flags=SRCALPHA, depth=32)  # 32-битная поверхность с прозрачностью, общие для всех Surface

# MAIN_SF - Поверхность с основной логикой, по центру, в пропорции кадра диафильма, [ [тут] ]
# Пропорция кадра диафильма (высота / ширина)
# основополагающая величина приложения
#     Размер кадра диафильма — 18×24 мм - 0,75
#     Полезное пространство — 17×23 мм - 0,74
#     На практике найдено
#         0.7713767593953097 все
#         0.6729159549157469 кроме w < 700 or h <500
MAIN_SF_PROPORTION = 0.74  # ширина больше высоты
MAIN_SF_WIDTH_PX = SCREEN_HEIGHT_PX // MAIN_SF_PROPORTION
MAIN_SF_HEIGHT_PX = SCREEN_HEIGHT_PX
MAIN_SF_LEFT_PX = SCREEN_WIDTH_PX // 2 - MAIN_SF_WIDTH_PX // 2
MAIN_SF_TOP_PX = 0
MAIN_SF_PADDING_PX = int(MAIN_SF_HEIGHT_PX * 0.03)  # отступ MAIN_SF считается относительно высоты

# меню логически разбито на линии, относительно MAIN_SF_HEIGHT_PX
MENU_LINE_1_H_COEF = 0.14  # хед
MENU_LINE_2_H_COEF = 0.33  # чекбоксы
MENU_LINE_3_H_COEF = 0.53  # кнопки и кадр

# сцены плеера
PLAYER_SCENE_ROOT = 1

# сцены меню
MENU_SCENE_ROOT = 11
MENU_SCENE_ABOUT = 12
MENU_SCENE_SEARCH = 13
