from random import choice, randint
from typing import Union

from pygame import BLEND_RGBA_MULT, Color, Surface, gfxdraw, transform
from pygame.transform import scale

from common_tools.consts import (
    DIR_ARROW_ALPHA,
    GRID_TRI_HEIGHT,
    GRID_TRI_WIDTH,
    INFO_AREA_HEIGHT,
    INFO_AREA_WIDTH,
    IS_ACTIVE,
    IS_STATIC,
    PLAY_AREA_HEIGHT,
    PLAY_AREA_WIDTH,
    SCREEN_HEIGHT_PX,
    SCREEN_WIDTH_PX,
    SPARK_SIZE_PX,
    SURFACE_ARGS,
)
from common_tools.i18n import I18N_SF_TEXT_GAME_RESULTS, I18N_START_GAME_GREETINGS
from common_tools.resources import (
    FONT_BIGTEXT,
    FONT_SCORE,
    FONT_SPEED,
    FONT_START_GAME_GREET,
    FONT_TEXT_ML,
    IMG_AREA_INFO,
    IMG_AREA_PLAY,
    IMG_ARROW,
    IMG_BORDER,
    IMG_INPUT,
    IMG_LOADING,
    IMG_TRI_GRID,
)
from common_tools.surface import (
    blit_rotated,
    colored_block_surface,
    shine_surface,
    text_ml_surface,
    text_surface,
    texture_onto_sf,
)


def _surface_triangle(color: str, reflect: bool) -> Surface:
    """Поверхность в форме треугольника"""
    width = int(SCREEN_WIDTH_PX * GRID_TRI_WIDTH)
    height = int(SCREEN_HEIGHT_PX * GRID_TRI_HEIGHT)
    surface = Surface((width, height), **SURFACE_ARGS)
    points = ((width / 2, 0), (0, height), (width, height), (width / 2, 0))
    # сглаживание
    gfxdraw.aapolygon(surface, points, Color(color))
    # основа
    gfxdraw.filled_polygon(surface, points, Color(color))
    # текстура
    tri = scale(IMG_TRI_GRID.convert_alpha(), surface.get_size())
    surface.blit(tri, (0, 0), special_flags=BLEND_RGBA_MULT)
    # отражение по вертикали
    surface = transform.flip(surface, False, reflect)
    return surface


def _surface_triangle_small(color: str, reflect: bool) -> Surface:
    """Поверхность в форме малого треугольника"""
    surface = _surface_triangle(color, reflect)
    w, h = surface.get_size()
    small_sf = scale(surface, (w / 2.2, h / 2.2))
    sw, sh = small_sf.get_size()
    res_sf = Surface((w, h), **SURFACE_ARGS)
    h_fx = h * 0.1 * (-1 if reflect else 1)
    res_sf.blit(small_sf, (w / 2 - sw / 2, h / 2 - sh / 2 + h_fx))
    return res_sf


def _surface_direction_arrow(rotation_angle: int) -> Surface:
    # основная текстура
    width = int(SCREEN_WIDTH_PX * GRID_TRI_WIDTH)
    height = int(SCREEN_HEIGHT_PX * GRID_TRI_HEIGHT)
    surface = scale(IMG_ARROW.convert_alpha(), (width, height))
    # поворот
    w, h = surface.get_size()
    new_sf = Surface((w, h), **SURFACE_ARGS)
    req_center_point = (w / 2, h / 2)
    blit_rotated(new_sf, surface, req_center_point, req_center_point, rotation_angle)
    surface = new_sf
    # рамка
    shine_size = int(height * 0.02)
    surface = shine_surface(surface, '#FFFFFF', shine_size, 255)
    # прозрачность
    surface.set_alpha(DIR_ARROW_ALPHA)
    return surface


def surface_spark(texture: Surface, alpha: int,
                  center_color_str: str, main_color_str: str, noise_color_str: str = None) -> Surface:
    """
    Поверхность затухающей искры
    alpha==0 это прозрачный, (0-255)
    """
    # основная текстура
    spark_sf = scale(texture.convert_alpha(), (SPARK_SIZE_PX, SPARK_SIZE_PX))
    spark_sf.set_alpha(alpha)

    # искра в виде вертикального крестика с точкой в центре
    if not (0 <= alpha <= 255):
        raise ValueError
    surface = Surface((3, 3), **SURFACE_ARGS)
    alpha_str = f'{alpha:x}'.zfill(2)
    surface.set_at((1, 1), Color(f'{center_color_str}{alpha_str}'))
    for main_point in ((1, 0), (0, 1), (1, 2), (2, 1)):
        surface.set_at(main_point, Color(f'{main_color_str}{alpha_str}'))
    if noise_color_str:
        surface.set_at((randint(0, 2), randint(0, 2)), Color(f'{noise_color_str}FF'))
    noise_ratio = 2
    surface = scale(surface, (SPARK_SIZE_PX // noise_ratio, SPARK_SIZE_PX // noise_ratio))

    # поворот искры
    w, h = surface.get_size()
    new_sf = Surface((w, h), **SURFACE_ARGS)
    req_center_point = (w / 2, h / 2)
    blit_rotated(new_sf, surface, req_center_point, req_center_point, randint(0, 359))
    surface = new_sf

    spark_sf.blit(surface, (randint(0, SPARK_SIZE_PX - w), randint(0, SPARK_SIZE_PX - h)))
    return spark_sf


def surface_info_area() -> Surface:
    # D7D7D7-single
    surface = colored_block_surface(
        Color('#ffffff'), width=int(SCREEN_WIDTH_PX * INFO_AREA_WIDTH), height=SCREEN_HEIGHT_PX * INFO_AREA_HEIGHT)
    return texture_onto_sf(IMG_AREA_INFO, surface, BLEND_RGBA_MULT)


def surface_play_area() -> Surface:
    # DCB78B-single
    surface = colored_block_surface(  # #ebd6be
        Color('#efdfcb'), width=int(SCREEN_WIDTH_PX * PLAY_AREA_WIDTH), height=SCREEN_HEIGHT_PX * PLAY_AREA_HEIGHT)
    return texture_onto_sf(IMG_AREA_PLAY, surface, BLEND_RGBA_MULT)


def surface_border() -> Surface:
    scaled_texture = scale(IMG_BORDER.convert_alpha(),
                           (int(SCREEN_WIDTH_PX * INFO_AREA_WIDTH), int(SCREEN_WIDTH_PX * INFO_AREA_HEIGHT * 0.15)))
    return scaled_texture


def surface_triangle_active_up() -> Surface:
    return _surface_triangle('#AE2E0B', False)


def surface_triangle_active_down() -> Surface:
    return _surface_triangle('#AE2E0B', True)


def surface_triangle_grid_up() -> Surface:
    return _surface_triangle('#f5ebd6', False)  # EEDDBB single


def surface_triangle_grid_down() -> Surface:
    return _surface_triangle('#f5ebd6', True)  # EEDDBB single


def surface_triangle_static_up() -> Surface:
    return _surface_triangle('#5C8072', False)


def surface_triangle_static_down() -> Surface:
    return _surface_triangle('#5C8072', True)


def surface_triangle_score_up() -> Surface:
    return _surface_triangle('#FFD700', False)


def surface_triangle_score_down() -> Surface:
    return _surface_triangle('#FFD700', True)


def surface_triangle_score_up_small() -> Surface:
    return _surface_triangle_small('#FFD700', False)


def surface_triangle_score_down_small() -> Surface:
    return _surface_triangle_small('#FFD700', True)


def surface_triangle_no_intersect_up() -> Surface:
    return _surface_triangle('#9932CC', False)


def surface_triangle_no_intersect_down() -> Surface:
    return _surface_triangle('#9932CC', True)


def surface_direction_arrow_left() -> Surface:
    return _surface_direction_arrow(-30)


def surface_direction_arrow_right() -> Surface:
    return _surface_direction_arrow(30)


def surface_label_pause() -> Surface:
    font_surface = text_surface(FONT_BIGTEXT, 'PAUSE', '#4682B4', '#8B4513')
    font_surface.set_alpha(int(255 * 0.8))
    return font_surface


def surface_label_game_over() -> Surface:
    font_color_game_over1 = '#B22222'
    font_color_game_over2 = '#ffcc7a'
    text1, text2, *more = 'GAME OVER'.split(' ')  # *шрифт без кириллицы
    font_surface1 = text_surface(FONT_BIGTEXT, text1, font_color_game_over1, font_color_game_over2)
    font_surface2 = text_surface(FONT_BIGTEXT, text2, font_color_game_over1, font_color_game_over2)
    fs1_w, fs1_h = font_surface1.get_size()
    fs2_w, fs2_h = font_surface2.get_size()
    line_dist = fs1_h * 0.1
    font_surface_res = Surface((max(fs1_w, fs2_w), max(fs1_h, fs2_h) * 2 + line_dist), **SURFACE_ARGS)
    font_surface_res.blit(font_surface1, (0, 0))
    font_surface_res.blit(font_surface2, (0, fs2_h + line_dist))
    font_surface_res.set_alpha(int(255 * 0.8))
    return font_surface_res


def surface_text_game_results(score: int) -> Surface:
    text = I18N_SF_TEXT_GAME_RESULTS.replace('SCORE', str(score))
    surface = text_ml_surface(FONT_TEXT_ML, text, '#696969', SCREEN_WIDTH_PX * 0.8)
    surface.set_alpha(int(255 * 0.95))
    return surface


def surface_input_player_name(input_state: int) -> Surface:
    if input_state == IS_STATIC:
        shine_color = '#FFD700'
    elif input_state == IS_ACTIVE:
        shine_color = '#7FFFD4'
    else:
        raise ValueError(f'wrong input_state: {input_state}')
    surface = colored_block_surface('#ffffff', SCREEN_WIDTH_PX * 0.7, FONT_TEXT_ML.get_linesize() * 2)
    surface = texture_onto_sf(IMG_INPUT, surface, BLEND_RGBA_MULT)
    surface = shine_surface(surface, '#333333', 2, 200)
    surface = shine_surface(surface, shine_color, int(FONT_TEXT_ML.get_linesize() * 0.3), 10)
    return surface


def surface_loading() -> Surface:
    return scale(IMG_LOADING.convert_alpha(), (SCREEN_WIDTH_PX, SCREEN_HEIGHT_PX))


def surface_full_screen_flash() -> Surface:
    return colored_block_surface('#FFFFFF', SCREEN_WIDTH_PX - 1, SCREEN_HEIGHT_PX - 1)  # *полоса внизу без -1


def surface_text_start_game_greet_popup() -> Surface:
    greet_text = choice([i.replace('_', '\n') for i in I18N_START_GAME_GREETINGS.splitlines() if i])
    return text_ml_surface(FONT_START_GAME_GREET, greet_text, '#800080', SCREEN_WIDTH_PX * 0.8, align_center=True)


def surface_text_speed(value: Union[int, str]) -> Surface:
    return text_surface(FONT_SPEED, value, '#4682B4', '#FFE4B5')


def surface_text_speed_popup(value: Union[int, str]) -> Surface:
    return text_surface(FONT_SPEED, value, '#800080', '#FFE4B5')


def surface_text_score(value: Union[int, str]) -> Surface:
    return text_surface(FONT_SCORE, value, '#FFD700', '#8B4513')
