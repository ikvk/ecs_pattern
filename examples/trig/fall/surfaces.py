from random import randint

from pygame import Color, Surface, gfxdraw, transform, BLEND_RGBA_MULT
from pygame.transform import scale

from common_tools.i18n import I18N_SF_TEXT_GAME_RESULTS
from common_tools.consts import INFO_AREA_WIDTH, PLAY_AREA_WIDTH, GRID_TRI_WIDTH, GRID_TRI_HEIGHT, \
    SCREEN_WIDTH, SCREEN_HEIGHT, INFO_AREA_HEIGHT, PLAY_AREA_HEIGHT, \
    FONT_COLOR_PAUSE1, FONT_COLOR_GAME_OVER1, FONT_COLOR_PAUSE2, FONT_COLOR_GAME_OVER2, \
    SPARK_SIZE_PX, SURFACE_ARGS, IS_ACTIVE, IS_STATIC
from common_tools.resources import FONT_BIGTEXT, IMG_AREA_INFO, IMG_AREA_PLAY, IMG_BORDER, IMG_TRI_GRID, FONT_TEXT_ML, \
    IMG_INPUT, IMG_LOADING
from common_tools.surface import texture_onto_sf, text_surface, colored_block_surface, text_ml_surface, shine_surface


def _surface_triangle(color: str, reflect: bool) -> Surface:
    """Поверхность в форме треугольника"""
    width = int(SCREEN_WIDTH * GRID_TRI_WIDTH)
    height = int(SCREEN_HEIGHT * GRID_TRI_HEIGHT)
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


def surface_spark(alpha: int, center_color_str: str, main_color_str: str, noise_color_str: str = None) -> Surface:
    """
    Поверхность в виде вертикального крестика с точкой в центре (Искра)
    alpha=0 - прозрачный
    """
    assert 0 <= alpha <= 255
    surface = Surface((3, 3), **SURFACE_ARGS)
    alpha_str = f'{alpha:x}'.zfill(2)
    surface.set_at((1, 1), Color(f'{center_color_str}{alpha_str}'))
    for main_point in ((1, 0), (0, 1), (1, 2), (2, 1)):
        surface.set_at(main_point, Color(f'{main_color_str}{alpha_str}'))
    if noise_color_str:
        surface.set_at((randint(0, 2), randint(0, 2)), Color(f'{noise_color_str}FF'))
    surface = scale(surface, (SPARK_SIZE_PX, SPARK_SIZE_PX))
    return surface


def surface_info_area() -> Surface:
    # D7D7D7-single
    surface = colored_block_surface(
        Color('#ffffff'), width=int(SCREEN_WIDTH * INFO_AREA_WIDTH), height=SCREEN_HEIGHT * INFO_AREA_HEIGHT)
    return texture_onto_sf(IMG_AREA_INFO, surface, BLEND_RGBA_MULT)


def surface_play_area() -> Surface:
    # DCB78B-single
    surface = colored_block_surface(  # #ebd6be
        Color('#efdfcb'), width=int(SCREEN_WIDTH * PLAY_AREA_WIDTH), height=SCREEN_HEIGHT * PLAY_AREA_HEIGHT)
    return texture_onto_sf(IMG_AREA_PLAY, surface, BLEND_RGBA_MULT)


def surface_border() -> Surface:
    scaled_texture = scale(IMG_BORDER.convert_alpha(),
                           (int(SCREEN_WIDTH * INFO_AREA_WIDTH), int(SCREEN_WIDTH * INFO_AREA_HEIGHT * 0.15)))
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


def surface_triangle_no_intersect_up() -> Surface:
    return _surface_triangle('#9932CC', False)


def surface_triangle_no_intersect_down() -> Surface:
    return _surface_triangle('#9932CC', True)


def surface_label_pause() -> Surface:
    font_surface = text_surface(FONT_BIGTEXT, 'PAUSE', FONT_COLOR_PAUSE1, FONT_COLOR_PAUSE2)
    font_surface.set_alpha(int(255 * 0.8))
    return font_surface


def surface_label_game_over() -> Surface:
    text1, text2, *more = 'GAME OVER'.split(' ')  # *шрифт без кириллицы
    font_surface1 = text_surface(FONT_BIGTEXT, text1, FONT_COLOR_GAME_OVER1, FONT_COLOR_GAME_OVER2)
    font_surface2 = text_surface(FONT_BIGTEXT, text2, FONT_COLOR_GAME_OVER1, FONT_COLOR_GAME_OVER2)
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
    surface = text_ml_surface(FONT_TEXT_ML, text, '#696969', SCREEN_WIDTH * 0.8)
    surface.set_alpha(int(255 * 0.95))
    return surface


def surface_input_player_name(input_state: int) -> Surface:
    if input_state == IS_STATIC:
        shine_color = '#FFD700'
    elif input_state == IS_ACTIVE:
        shine_color = '#7FFFD4'
    else:
        raise ValueError(f'wrong input_state: {input_state}')
    surface = colored_block_surface('#ffffff', SCREEN_WIDTH * 0.7, FONT_TEXT_ML.get_linesize() * 2)
    surface = texture_onto_sf(IMG_INPUT, surface, BLEND_RGBA_MULT)
    surface = shine_surface(surface, '#333333', 2, 200)
    surface = shine_surface(surface, shine_color, int(FONT_TEXT_ML.get_linesize() * 0.3), 10)
    return surface


def surface_loading() -> Surface:
    return scale(IMG_LOADING.convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))
