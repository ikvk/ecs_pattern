from typing import Tuple

from pygame import Surface
from pygame.transform import scale

from common_tools.consts import SCREEN_WIDTH, SCREEN_HEIGHT, SURFACE_ARGS, SHINE_SIZE, SNOWFLAKE_ANIMATION_FRAMES
from common_tools.resources import IMG_SHINE, IMG_SNOWFLAKE, IMG_BACKGROUND
from common_tools.surface import blit_rotated


def surface_background() -> Surface:
    return scale(IMG_BACKGROUND.convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))


def surface_shine() -> Surface:
    return scale(IMG_SHINE.convert_alpha(), (SCREEN_HEIGHT * SHINE_SIZE, SCREEN_HEIGHT * SHINE_SIZE))


def surface_snowflake_animation_set(snowflake_scale: str, snowflake_alpha: int, reverse: bool) -> Tuple[Surface, ...]:
    snowflake_size = SCREEN_HEIGHT * snowflake_scale
    snowflake_sf = scale(IMG_SNOWFLAKE.convert_alpha(), (snowflake_size, snowflake_size))

    snowflake_frames = []
    snowflake_frame_cnt = SNOWFLAKE_ANIMATION_FRAMES  # кадров в полном повороте от 0 до 360 градусов
    for i in range(snowflake_frame_cnt):
        _angle = int(360 / snowflake_frame_cnt) * i
        new_sf = Surface((snowflake_size, snowflake_size), **SURFACE_ARGS).convert_alpha()
        req_center_point = (snowflake_size / 2, snowflake_size / 2)
        blit_rotated(new_sf, snowflake_sf, req_center_point, req_center_point, _angle)
        new_sf.set_alpha(snowflake_alpha)  # 255 непрозрачный
        snowflake_frames.append(new_sf)
    return tuple((reversed if reverse else lambda x: x)(snowflake_frames))
