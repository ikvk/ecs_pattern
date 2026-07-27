"""
Путь к файлам ресурсов должен быть без пробелов и состоять из латинских символов
На android нужно использовать bytes_buffer_instead_path
"""
import warnings

from pygame import Surface
from pygame.font import Font
from pygame.image import load

from common_tools.compatibility import bytes_buffer_instead_path
from common_tools.consts import  MAIN_SF_HEIGHT_PX, SCREEN_HEIGHT_PX
from common_tools.surface import colored_block_surface


def load_font(path: str, size: int) -> Font:
    """Загрузить шрифт из файла"""
    try:
        return Font(bytes_buffer_instead_path(path), size)
    except FileNotFoundError:
        warnings.warn(f'Font not found: {path}', stacklevel=2)
        return Font(None, int(SCREEN_HEIGHT_PX / 13))  # None - default font


def load_img(path: str) -> Surface:
    """Загрузить изображение из файла"""
    try:
        return load(bytes_buffer_instead_path(path))
    except FileNotFoundError:
        warnings.warn(f'Image not found: {path}', stacklevel=2)
        return colored_block_surface('#FF00FFaa', 100, 100)


# объекты изображений
IMG_ICON_DICE = load_img('res/img/icon_dice.png')  # иконка - кубик
IMG_ICON_FLAG_1 = load_img('res/img/icon_flag_1.png')  # иконка - 1 чекбокса типовая
IMG_ICON_FLAG_0 = load_img('res/img/icon_flag_0.png')  # иконка - 0 чекбокса
IMG_UI_BUTTON = load_img('res/img/ui_button.png')  # кнопка с текстом - прямоугольная
IMG_UI_BUTTON_SMALL = load_img('res/img/ui_button_small.png')  # кнопка только с иконкой - квадратная
IMG_UI_CHECKBOX = load_img('res/img/ui_checkbox.png')  # чекбокс
IMG_UI_CIRCLE = load_img('res/img/ui_circle.png')  # шарик скролла
IMG_UI_FRAME = load_img('res/img/ui_frame.png')  # рамка кадра
IMG_UI_HEAD = load_img('res/img/ui_head.png')  # подложка заголовка
IMG_UI_INPUT = load_img('res/img/ui_input.png')  # подложка поля ввода

# объекты шрифтов - Font
FONT_DEFAULT = Font(None, int(MAIN_SF_HEIGHT_PX / 35))  # служебный, например для FPS
_alice_path = 'res/font/Alice/Alice-Regular.ttf'
FONT_UI_BUTTON = load_font(_alice_path, int(MAIN_SF_HEIGHT_PX / 33))  # шрифт кнопок
FONT_UI_CHECKBOX = load_font(_alice_path, int(MAIN_SF_HEIGHT_PX / 36))  # шрифт чекбоксов
FONT_UI_INPUT = load_font(_alice_path, int(MAIN_SF_HEIGHT_PX / 35))  # шрифт инпутов
FONT_UI_TEXT = load_font(_alice_path, int(MAIN_SF_HEIGHT_PX / 28))  # шрифт текстовых блоков вне контролов
FONT_UI_TEXT_HEADER = load_font(_alice_path, int(MAIN_SF_HEIGHT_PX / 20))  # заголовок приложения
