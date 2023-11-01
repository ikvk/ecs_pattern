from typing import Any, Optional, Union

from pygame.transform import rotate, scale
from pygame.draw import rect
from pygame.math import Vector2
from pygame.font import Font
from pygame import Color, Surface, BLEND_RGBA_MULT

from .consts import SURFACE_ARGS


def blit_rotated(surf: Surface, image: Surface, pos, origin_pos, angle: int, fill_color=(0, 0, 0, 0)):
    """
    Вывести на surf изображение image, повернутое вокруг pos на angle градусов
    surf: target Surface
    image: Surface which has to be rotated and blit
    pos: position of the pivot on the target Surface surf (relative to the top left of surf)
    origin_pos: position of the pivot on the image Surface (relative to the top left of image)
    angle: angle of rotation in degrees
    """
    # offset from pivot to center
    image_rect = image.get_rect(topleft=(pos[0] - origin_pos[0], pos[1] - origin_pos[1]))
    offset_center_to_pivot = Vector2(pos) - image_rect.center
    # rotated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
    # get a rotated image
    rotated_image = rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)
    # rotate and blit the image
    surf.blit(rotated_image, rotated_image_rect)
    # draw rectangle around the image
    rect(surf, fill_color, (*rotated_image_rect.topleft, *rotated_image.get_size()), 2)


def colorize_surface(surface: Surface, color: str) -> Surface:
    colorized_surface = Surface(surface.get_size(), **SURFACE_ARGS)
    colorized_surface.fill(Color(color))
    res_surface = surface.copy()
    res_surface.blit(colorized_surface, (0, 0), special_flags=BLEND_RGBA_MULT)
    return res_surface


def texture_onto_sf(texture: Surface, surface: Surface, special_flags: int) -> Surface:
    """Масштабировать и наложить текстуру на поверхность"""
    scaled_texture = scale(texture.convert_alpha(), surface.get_size())
    surface.blit(scaled_texture, (0, 0), special_flags=special_flags)
    return surface


def text_surface(font_obj: Font, value: Any, color_main: str, color_shadow: Optional[str] = None,
                 shadow_shift: float = 0.03) -> Surface:
    """Создать поверхность с текстом"""
    surface_main = font_obj.render(str(value), True, Color(color_main))
    if not color_shadow:
        return surface_main
    surface_shadow = font_obj.render(str(value), True, Color(color_shadow))
    w, h = surface_main.get_size()
    shadow_dx = shadow_dy = int(h * shadow_shift)
    surface_res = Surface((w + shadow_dx, h + shadow_dy), **SURFACE_ARGS)
    surface_res.blit(surface_shadow, (shadow_dx, shadow_dy))
    surface_res.blit(surface_main, (0, 0))
    return surface_res


def text_ml_surface(font_obj: Font, ml_text: str, color: str, width: float, linesize_rate: float = 1.0) -> Surface:
    """Создать поверхность с многострочным текстом"""
    words_by_lines = [line.split(' ') for line in ml_text.splitlines()]
    space_width = font_obj.size(' ')[0]
    color_obj = Color(color)
    font_line_height = font_obj.get_linesize() * linesize_rate

    # get height
    x, y = 0, 0
    for line in words_by_lines:
        for word in line:
            word_width = font_obj.size(word)[0]
            if x + word_width >= width:
                x = 0
                y += font_line_height
            x += word_width + space_width
        x = 0
        y += font_line_height

    # render
    surface = Surface((width, y), **SURFACE_ARGS)
    x, y = 0, 0
    for line in words_by_lines:
        for word in line:
            word_surface = font_obj.render(word, True, color_obj)
            word_width = word_surface.get_size()[0]
            if x + word_width >= width:
                x = 0
                y += font_line_height
            surface.blit(word_surface, (x, y))
            x += word_width + space_width
        x = 0
        y += font_line_height

    return surface


def colored_block_surface(color: Union[Color, int, str], width: int, height: int):
    """Квадратная поверхность с заданным цветом и размером"""
    surface = Surface((width, height), **SURFACE_ARGS)
    surface.fill(color)
    return surface
