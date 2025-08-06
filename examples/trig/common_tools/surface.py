from functools import cache
from typing import Any, List, Optional, Tuple, Union

from pygame import BLEND_RGBA_MULT, Color, Surface, mask
from pygame.draw import rect
from pygame.font import Font
from pygame.math import Vector2
from pygame.transform import rotate, scale, smoothscale

from common_tools.consts import SURFACE_ARGS


@cache
def _circle_points(r: int) -> List[Tuple[int, int]]:
    r = int(round(r))
    x, y, e = r, 0, 1 - r
    points = []
    while x >= y:
        points.append((x, y))
        y += 1
        if e < 0:
            e += 2 * y - 1
        else:
            x -= 1
            e += 2 * (y - x) - 1
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    points.sort()
    return points


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


def text_ml_surface(font_obj: Font, ml_text: str, color: str, width: float,
                    linesize_rate: float = 1.0, align_center: bool = False) -> Surface:
    """Создать поверхность с многострочным текстом"""
    words_by_lines = [line.split(' ') for line in ml_text.splitlines()]
    space_width = font_obj.size(' ')[0]
    color_obj = Color(color)
    font_line_height = font_obj.get_linesize() * linesize_rate

    # Сборка строк с соблюдением ширины
    rendered_lines = []
    for line_words in words_by_lines:
        current_line = []
        current_width = 0
        for word in line_words:
            word_width = font_obj.size(word)[0]
            if current_width + word_width >= width:
                rendered_lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width + space_width
            else:
                current_line.append(word)
                current_width += word_width + space_width
        if current_line:
            rendered_lines.append(' '.join(current_line))

    # Расчет общей высоты текста
    total_height = len(rendered_lines) * font_line_height

    # Создание поверхности
    surface = Surface((width, total_height), **SURFACE_ARGS)
    y_pos = 0

    # Рисуем текст с учётом выбранного выравнивания
    for line in rendered_lines:
        line_surface = font_obj.render(line, True, color_obj)
        line_width = line_surface.get_width()
        x_pos = (width - line_width) / 2 if align_center else 0  # Центрирование строки, если требуется
        surface.blit(line_surface, (x_pos, y_pos))
        y_pos += font_line_height

    return surface


def colored_block_surface(color: Union[Color, int, str], width: int, height: int):
    """Квадратная поверхность с заданным цветом и размером"""
    surface = Surface((width, height), **SURFACE_ARGS)
    surface.fill(color)
    return surface


def outline(surface: Surface, color_str: str, size_px: int, alpha: int = 255) -> Surface:
    """Создать обводку поверхности указанной толщины и прозрачности"""
    mask_sf = mask.from_surface(surface).to_surface()
    mask_sf.set_colorkey(0)
    mask_sf.convert_alpha()
    mask_sf = colorize_surface(mask_sf, color_str)
    w, h = surface.get_size()
    res_sf = Surface((w + size_px * 2, h + size_px * 2), **SURFACE_ARGS)
    for dx, dy in _circle_points(size_px):
        res_sf.blit(mask_sf, (dx + size_px, dy + size_px))
    res_sf.set_alpha(alpha)
    return res_sf


def shine_surface(surface: Surface, color_str: str, size_px: int, shine_sf_alpha: int, alt_size: int = None) -> Surface:
    """
    Добавить внешнее сияние для заданной поверхности
    alt_size для оптимизации скорости
    """
    sw, sh = surface.get_size()
    res_sf = Surface((sw + size_px * 2, sh + size_px * 2), **SURFACE_ARGS)
    for i in range(1, (alt_size or size_px) + 1):
        outline_sf = outline(surface, color_str, i, shine_sf_alpha)
        res_sf.blit(outline_sf, (size_px - i, size_px - i))
    res_sf.blit(surface, (size_px, size_px))
    return res_sf


def gaussian_blur(surface: Surface, radius: float):
    scaled_surface = smoothscale(surface, (surface.get_width() // radius, surface.get_height() // radius))
    scaled_surface = smoothscale(scaled_surface, (surface.get_width(), surface.get_height()))
    return scaled_surface
