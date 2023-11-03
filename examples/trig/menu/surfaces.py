from typing import Tuple

from pygame import Surface, BLEND_RGBA_MULT
from pygame.transform import scale

from common_tools.consts import SCREEN_WIDTH, SURFACE_ARGS, MENU_SHINE_WIDTH, SCREEN_HEIGHT, TEXT_ML_WIDTH, \
    SETTINGS_STORAGE, GAME_NAME, GAME_VERSION, PACKAGE_EDITION, PACKAGE_EDITION_FREE
from common_tools.resources import IMG_LIGHT_SHINE, FONT_MENU_GAME_NAME, FONT_TEXT_ML, IMG_GAME_NAME_BG, IMG_MENU_BG
from common_tools.i18n import I18N_SF_TEXT_RECORDS, I18N_SF_TEXT_ABOUT, I18N_SF_TEXT_GUIDE, I18N_SF_TEXT_SETTINGS, \
    SETTING_GRAPHIC_CAPTION, SETTING_SOUND_CAPTION, SETTING_LANGUAGE_CAPTION, SETTING_SCREEN_MODE_CAPTION, \
    I18N_SF_TEXT_FREE_VERSION
from common_tools.surface import blit_rotated, colorize_surface, texture_onto_sf, text_surface, text_ml_surface, \
    shine_surface


def _text_ml_surface(text: str) -> Surface:
    return text_ml_surface(FONT_TEXT_ML, text, '#696969', SCREEN_WIDTH * TEXT_ML_WIDTH)


def surface_shine_animation_set(color: str) -> Tuple[Surface, ...]:
    """Набор кадров анимации сияния с указанным цветом"""
    shine_w = shine_h = SCREEN_WIDTH * MENU_SHINE_WIDTH
    img_light_shine = scale(IMG_LIGHT_SHINE.convert_alpha(), (shine_w, shine_h))

    shine_frames = []
    shine_alpha_min = int(255 * 0.38)  # мин. непрозрачность
    shine_alpha_max = int(255 * 0.0)  # макс. непрозрачность
    shine_frame_cnt = 80  # от 0 до 360 градусов
    _ratio = (shine_alpha_min - shine_alpha_max) / shine_frame_cnt * 2
    _half_shine_bloom_val_set = []
    for i in range(int(shine_frame_cnt / 2)):
        _half_shine_bloom_val_set.append(int(shine_alpha_min - i * _ratio))
    shine_bloom_val_set = list(reversed(_half_shine_bloom_val_set)) + _half_shine_bloom_val_set
    for i in range(shine_frame_cnt):
        res_sf = Surface((shine_w, shine_h), **SURFACE_ARGS).convert_alpha()
        _angle = int(360 / shine_frame_cnt) * i
        for angle in (_angle, -_angle):
            new_sf = Surface((shine_w, shine_h), **SURFACE_ARGS).convert_alpha()
            req_center_point = (shine_w / 2, shine_h / 2)
            blit_rotated(new_sf, img_light_shine, req_center_point, req_center_point, angle)
            new_sf.set_alpha(shine_bloom_val_set[i])  # 255 непрозрачный
            res_sf.blit(colorize_surface(new_sf, color), (0, 0))
        shine_frames.append(res_sf)

    return tuple(shine_frames)


def surface_background() -> Surface:
    return scale(IMG_MENU_BG.convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))


def surface_label_game_name() -> Surface:
    font_sf = text_surface(FONT_MENU_GAME_NAME, 'Trig fall', '#FFD700')
    shine_size = int(FONT_MENU_GAME_NAME.get_height() * 0.05)
    shine_sf = shine_surface(font_sf, '#111111', shine_size, 15)
    textured_font_sf = texture_onto_sf(IMG_GAME_NAME_BG, font_sf, BLEND_RGBA_MULT)
    shine_sf.blit(textured_font_sf, (shine_size, shine_size))
    return shine_sf


def surface_input_name() -> Surface:
    pass


def surface_text_about() -> Surface:
    return _text_ml_surface(
        GAME_NAME.upper() +
        I18N_SF_TEXT_ABOUT.replace('GAME_VERSION', GAME_VERSION)
    )


def surface_text_records() -> Surface:
    if PACKAGE_EDITION == PACKAGE_EDITION_FREE:
        text = I18N_SF_TEXT_FREE_VERSION
    else:
        text = '\n'.join([f' § {score} • {name} • {dt}' for score, name, dt in SETTINGS_STORAGE.records])
    return _text_ml_surface(
        GAME_NAME.upper() +
        I18N_SF_TEXT_RECORDS +
        text
    )


def surface_text_guide() -> Surface:
    return _text_ml_surface(
        GAME_NAME.upper() +
        I18N_SF_TEXT_GUIDE
    )


def surface_text_settings() -> Surface:
    text = \
        GAME_NAME.upper() + \
        I18N_SF_TEXT_SETTINGS.replace(
            'GRAPHIC_CAPTION', SETTING_GRAPHIC_CAPTION[SETTINGS_STORAGE.graphic]
        ).replace(
            'SCREEN_MODE_CAPTION', SETTING_SCREEN_MODE_CAPTION[SETTINGS_STORAGE.screen_mode]
        ).replace(
            'SOUND_CAPTION', SETTING_SOUND_CAPTION[SETTINGS_STORAGE.sound]
        ).replace(
            'LANGUAGE_CAPTION', SETTING_LANGUAGE_CAPTION[SETTINGS_STORAGE.language]
        )
    return text_ml_surface(FONT_TEXT_ML, text, '#696969', SCREEN_WIDTH * TEXT_ML_WIDTH)
