from pygame import Surface
from pygame.transform import smoothscale

from common_tools.consts import (
    MAIN_SF_HEIGHT_PX,
    MAIN_SF_WIDTH_PX,
    SCREEN_HEIGHT_PX,
    SCREEN_WIDTH_PX,
    settings_storage,
)
from common_tools.resources import load_frame
from common_tools.surface import colored_block_surface


def surface_player_background() -> Surface:
    """Для PlayerBackground"""
    return colored_block_surface('#333333ff', SCREEN_WIDTH_PX, SCREEN_HEIGHT_PX)


def surface_current_film_frame() -> Surface:
    """Выбранный кадр диафильма"""
    fid = settings_storage.current_film
    frame = settings_storage.current_frame
    return smoothscale(
        load_frame(fid, frame).convert_alpha(), (MAIN_SF_WIDTH_PX, MAIN_SF_HEIGHT_PX))
