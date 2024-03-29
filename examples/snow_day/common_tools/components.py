from typing import Tuple
from dataclasses import field

from pygame import Surface
from ecs_pattern import component


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
    frame_w: int = field(init=False)
    frame_h: int = field(init=False)

    def __post_init__(self):
        self.frame_w = self.frames[0].get_width()
        self.frame_h = self.frames[0].get_height()


@component
class ComAnimated:
    """Анимированный объект"""
    animation_set: ComAnimationSet  # набор кадров анимации, 0-последний кадр, len(animation_set)-первый кадр
    animation_looped: bool  # анимация зациклена либо удаляется после прохода
    animation_frame: int  # текущий кадр анимации, значение вычитается
    animation_frame_float: float  # для расчета переключения animation_frame
    animation_speed: float  # кадров в секунду, *используй поправку на FPS
