"""
Путь к файлам ресурсов должен быть без пробелов и состоять из латинских символов
На android нужно использовать bytes_buffer_instead_path
"""
import warnings

from pygame import Surface
from pygame.font import Font
from pygame.image import load
from pygame.mixer import Sound

from common_tools.compatibility import bytes_buffer_instead_path
from common_tools.consts import SCREEN_HEIGHT_PX, SCREEN_WIDTH_PX, SOUND_LEVEL
from common_tools.surface import colored_block_surface


def _load_font(path: str, size: int) -> Font:
    """Загрузить шрифт из файла"""
    try:
        return Font(bytes_buffer_instead_path(path), size)
    except FileNotFoundError:
        warnings.warn(f'Font not found: {path}', stacklevel=2)
        return Font(None, int(SCREEN_HEIGHT_PX / 13))  # None - default font


def _load_img(path: str) -> Surface:
    """Загрузить изображение из файла"""
    try:
        return load(bytes_buffer_instead_path(path))
    except FileNotFoundError:
        warnings.warn(f'Image not found: {path}', stacklevel=2)
        return colored_block_surface('#FF00FFff', 100, 100)


def _load_sound(path: str) -> Sound:
    """Загрузить изображение из файла"""
    try:
        return Sound(bytes_buffer_instead_path(path))
    except FileNotFoundError:
        warnings.warn(f'Sound not found: {path}', stacklevel=2)
        return Sound(bytes_buffer_instead_path('res/sound/_silence.ogg'))


# объекты изображений
IMG_TRI_GRID = _load_img('res/img/stone_sand_light.png')  # фон тругольников
IMG_AREA_PLAY = _load_img('res/img/sand1.jpg')  # фон под треугольниками - игровое поле
IMG_AREA_INFO = _load_img('res/img/stone_gray.jpg')  # фон инфо игры с цифрами - хед
IMG_BORDER = _load_img('res/img/border.png')  # граница между хедом и иговым полем
IMG_SPARK_LIGHT = _load_img('res/img/spark1.png')  # искра для светлой вспышки
IMG_SPARK_DARK = _load_img('res/img/spark2.png')  # искра для темной вспышки
IMG_ARROW = _load_img('res/img/arrow.png')  # стрелка направления движения фигуры
#
IMG_MENU_BG = _load_img('res/img/menu_bg.jpg')
IMG_LOADING = _load_img('res/img/loading.jpg')
IMG_GAME_NAME_BG = _load_img('res/img/game_name_bg.jpg')
IMG_LIGHT_SHINE = _load_img('res/img/light_shine.png')  # stone_sand_dark.jpg
IMG_DUST = _load_img('res/img/dust.png')  # пылинка
IMG_BUTTON_ROOT_1 = _load_img('res/img/button_root_1.png')
IMG_BUTTON_ROOT_2 = _load_img('res/img/button_root_2.png')
IMG_BUTTON_ROOT_3 = _load_img('res/img/button_root_3.png')
IMG_BUTTON_ROOT_4 = _load_img('res/img/button_root_4.png')
IMG_BUTTON_ROOT_5 = _load_img('res/img/button_root_5.png')
IMG_BUTTON_ROOT_6 = _load_img('res/img/button_root_6.png')
IMG_BUTTON_RECT = _load_img('res/img/button_rect.png')
IMG_INPUT = _load_img('res/img/input_bg.png')
IMG_ICON_ABOUT = _load_img('res/img/icon_about.png')
IMG_ICON_EXIT = _load_img('res/img/icon_exit.png')
IMG_ICON_GUIDE = _load_img('res/img/icon_guide.png')
IMG_ICON_RECORDS = _load_img('res/img/icon_records.png')
IMG_ICON_SETTINGS = _load_img('res/img/icon_settings.png')
IMG_ICON_PLAY = _load_img('res/img/icon_play.png')

# объекты шрифтов - Font
_faster_one_path = 'res/font/FasterOne/FasterOne-Regular.ttf'
_devinne_swash_path = 'res/font/DevinneSwash/DevinneSwash.ttf'
_alice_path = 'res/font/Alice/Alice-Regular.ttf'
FONT_DEFAULT = Font(None, int(SCREEN_HEIGHT_PX / 35))
FONT_SPEED = _load_font(_faster_one_path, int(SCREEN_HEIGHT_PX / 20))
FONT_SCORE = _load_font(_devinne_swash_path, int(SCREEN_HEIGHT_PX / 17))
FONT_BIGTEXT = _load_font(_devinne_swash_path, int(SCREEN_HEIGHT_PX / 10))
FONT_MENU_GAME_NAME = _load_font(_devinne_swash_path, int(SCREEN_WIDTH_PX / 5.5))
FONT_BUTTON = _load_font(_alice_path, int(SCREEN_WIDTH_PX / 20))
FONT_TEXT_ML = _load_font(_alice_path, int(SCREEN_HEIGHT_PX / 40))
FONT_START_GAME_GREET = _load_font(_alice_path, int(SCREEN_HEIGHT_PX / 30))

# *после шрифта есть пустое место
FONT_SPEED_HEIGHT_PX = FONT_SPEED.get_linesize()
FONT_SCORE_HEIGHT_PX = FONT_SCORE.get_linesize()
FONT_BIGTEXT_HEIGHT_PX = FONT_BIGTEXT.get_linesize()

# звуки
SOUND_MENU = _load_sound('res/sound/earth_qual0.ogg')
SOUND_TEXT_INPUT = _load_sound('res/sound/stone_on_stone_high.ogg')
SOUND_BUTTON_CLICK = _load_sound('res/sound/stone_on_stone_low.ogg')
SOUND_GAME_OVER = _load_sound('res/sound/game_over.ogg')
SOUND_PAUSE = _load_sound('res/sound/pause.ogg')
SOUND_SCORE = _load_sound('res/sound/score_ring.ogg')
SOUND_ROTATE = _load_sound('res/sound/rotate.ogg')
SOUND_CLEAN_LINE = _load_sound('res/sound/stone_break.ogg')
SOUND_SHIFT = _load_sound('res/sound/shift.ogg')
SOUND_START = _load_sound('res/sound/start.ogg')
SOUND_GAME_SPEED_UP = _load_sound('res/sound/game_speed_up.ogg')
SOUND_FAST_FALL = _load_sound('res/sound/fast_fall.ogg')
SOUND_CHANGE_DIR = _load_sound('res/sound/stone_on_stone_high.ogg')  # sand_hit.ogg
SOUND_EVENT_NO_INTERSECT = _load_sound('res/sound/event_no_intersect.ogg')
SOUND_FIGURE_DROP = _load_sound('res/sound/stone_on_stone_low.ogg')
SOUND_DENY = _load_sound('res/sound/deny.ogg')


def set_sound_volume(value: str):
    """Установить громкость всех звуков"""
    sound_all = (
        SOUND_MENU, SOUND_TEXT_INPUT, SOUND_BUTTON_CLICK, SOUND_GAME_OVER, SOUND_PAUSE, SOUND_SCORE, SOUND_ROTATE,
        SOUND_CLEAN_LINE, SOUND_SHIFT, SOUND_START, SOUND_GAME_SPEED_UP, SOUND_FAST_FALL,
        SOUND_EVENT_NO_INTERSECT, SOUND_CHANGE_DIR, SOUND_FIGURE_DROP, SOUND_DENY
    )
    sound_correction_map = {
        SOUND_MENU: 0.7,  # фоновая музыка в меню
        SOUND_TEXT_INPUT: 1,  # печать символа в поле ввода
        SOUND_CHANGE_DIR: 0.55,  # смена направления падения фигуры (ударом об стену или игроком)
        SOUND_BUTTON_CLICK: 1,  # клик кнопки меню
        SOUND_FIGURE_DROP: 1,  # фигура упала
        SOUND_GAME_OVER: 2,  # музыка окончания игры
        SOUND_PAUSE: 0.9,  # пауза в игре
        SOUND_SCORE: 1.5,  # получены очки
        SOUND_ROTATE: 0.4,  # поворот фигуры
        SOUND_CLEAN_LINE: 1.5,  # очистка заполненной линии
        SOUND_SHIFT: 0.4,  # сдвиг фигуры влево или вправо
        SOUND_START: 2,  # музыка старта игры
        SOUND_GAME_SPEED_UP: 1,  # повышена скорость игры
        SOUND_FAST_FALL: 0.15,  # запуск ускоренного падения фигуры
        SOUND_EVENT_NO_INTERSECT: 1.5,  # включение режима падения без препятствий
        SOUND_DENY: 1,  # клик на выключенный контрол меню
    }
    if len(sound_all) != len(sound_correction_map):
        raise ValueError
    # общий базовый уровень
    for i in sound_all:
        i.set_volume(SOUND_LEVEL[value])

    # настройка отдельных звуков
    for sound, volume_rate in sound_correction_map.items():
        sound.set_volume(sound.get_volume() * volume_rate)
