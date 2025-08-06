from typing import Callable, Hashable, Tuple

from ecs_pattern import component
from pygame import Rect, Surface
from pygame.font import Font

from common_tools.consts import BS_STATIC, IS_STATIC


@component
class ComLiveTime:
    """Время жизни до указанной секунды"""
    live_until_time: float  # когда время monotonic станет больше, объект удаляется


@component
class ComSurface:
    """Поверхность (изображение)"""
    surface: Surface


@component
class Com2dCoord:
    """Двухмерные координаты"""
    x: float  # X координата на дисплее, 0 слева
    y: float  # Y координата на дисплее, 0 сверху


@component
class ComSpeed:
    """Скорость перемещения"""
    speed_x: float  # пикселей в секунду, *используй поправку на FPS
    speed_y: float  # пикселей в секунду, *используй поправку на FPS


@component
class ComAnimationSet:
    """Набор поверхностей для анимации"""
    frames: Tuple[Surface]


@component
class ComAnimated:
    """Анимированный объект"""
    animation_set: ComAnimationSet  # набор кадров анимации, 0-последний кадр, len(animation_set)-первый кадр
    animation_looped: bool  # анимация зациклена либо удаляется после прохода
    animation_frame: int  # текущий кадр анимации, значение ВЫЧИТАЕТСЯ
    animation_frame_float: float  # для расчета переключения animation_frame
    animation_speed: float  # кадров в секунду, *используй поправку на FPS


@component
class _ComUiElement:
    """Общие свойства элементов графического интерфейса"""
    rect: Rect  # Rect(left, top, width, height), у контролов разные поверхности - для движения мыши
    scenes: [Hashable, ...]  # на каких сценах отображать


@component
class ComUiButton(_ComUiElement):
    """Элемент графического интерфейса - кнопка"""
    sf_static: Surface
    sf_hover: Surface = None
    sf_pressed: Surface = None
    mask: Surface = None  # активная область
    on_click: Callable = lambda: None
    state: int = BS_STATIC  # см. BS_NAME


@component
class ComUiInput(_ComUiElement):
    """Элемент графического интерфейса - поле ввода текста"""
    font: Font
    max_length: int
    sf_static: Surface
    sf_active: Surface = None
    mask: Surface = None  # активная область
    text: str = ''  # текст в поле ввода
    cursor: int = 0
    on_confirm: Callable = lambda: None  # подтверждение ввода - enter, графический ввод android
    on_edit: Callable = lambda: None  # изменение текста
    state: int = IS_STATIC  # см. IS_NAMES


@component
class ComUiText(_ComUiElement):
    """Элемент графического интерфейса - многострочный текст с прокруткой"""
    sf_text: Surface
    sf_bg: Surface
    scroll_pos: float = 0.0  # от 0 до 1
