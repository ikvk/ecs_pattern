from pygame import Color, Surface
from pygame.transform import smoothscale

from common_tools.consts import (
    DUST_SIZE_PX,
    MAIN_SF_HEIGHT_PX,
    MAIN_SF_PADDING_PX,
    MAIN_SF_PROPORTION,
    MAIN_SF_WIDTH_PX,
    MENU_LINE_1_H_COEF,
    MENU_LINE_3_H_COEF,
    PROJECT_VERSION,
    SCREEN_HEIGHT_PX,
    SCREEN_WIDTH_PX,
    SURFACE_ARGS,
)
from common_tools.i18n import (
    I18N_SF_TEXT_ABOUT_FROM_AUTHOR,
    I18N_SF_TEXT_ABOUT_PLAYER,
    I18N_SF_TEXT_ABOUT_RESOURCES,
    I18N_SF_TEXT_SEARCH_BY_ARTIST,
    I18N_SF_TEXT_SEARCH_BY_NAME,
    I18N_SF_TEXT_SEARCH_FOUND,
    I18N_SF_TEXT_SELECTED_FILMS,
)
from common_tools.resources import (
    FONT_UI_TEXT,
    FONT_UI_TEXT_ABOUT,
    FONT_UI_TEXT_HEADER,
    IMG_BG_MENU,
    IMG_UI_FRAME,
    IMG_UI_HEAD,
    load_frame,
)
from common_tools.surface import colored_block_surface, text_surface, text_surface_ml


def _text_surface_ml_3col(text: str) -> Surface:
    """Для about текстов - текст с фоном"""
    pad = MAIN_SF_PADDING_PX * 0.5
    res_sf = Surface((MAIN_SF_WIDTH_PX / 3, MAIN_SF_HEIGHT_PX), **SURFACE_ARGS)
    bg_sf = colored_block_surface('#FFF8DCf8', MAIN_SF_WIDTH_PX / 3 - pad * 2, MAIN_SF_HEIGHT_PX - pad * 2)
    text_sf = text_surface_ml(FONT_UI_TEXT_ABOUT, text, '#333333', MAIN_SF_WIDTH_PX / 3 - pad * 4)
    bg_sf.blit(text_sf, (pad, pad))
    res_sf.blit(bg_sf, (pad, pad))
    return res_sf


def surface_header() -> Surface:
    """Для Header"""
    width = MAIN_SF_WIDTH_PX
    height = MAIN_SF_HEIGHT_PX * MENU_LINE_1_H_COEF
    pad_h = 0.15
    back_sf = Surface((width, height), **SURFACE_ARGS)
    main_sf = smoothscale(IMG_UI_HEAD.convert_alpha(), (width, height * (1 - pad_h * 2)))
    back_sf.blit(main_sf, (0, height * pad_h))
    text_sf = text_surface(FONT_UI_TEXT_HEADER, 'Диафильмы', '#4682B4', '#FFE4B5')
    back_sf.blit(text_sf, (width / 2 - text_sf.get_width() / 2, height / 2 - text_sf.get_height() / 2))
    return back_sf


def surface_main_frame_border() -> Surface:
    """Для FrameBorder - рамка"""
    height = int(MAIN_SF_HEIGHT_PX * MENU_LINE_3_H_COEF)
    width = int(height // MAIN_SF_PROPORTION)
    back_sf = Surface((width, height), **SURFACE_ARGS)
    main_sf = smoothscale(IMG_UI_FRAME.convert_alpha(), (width, height * 0.97))
    back_sf.blit(main_sf, (0, 0))
    return back_sf


def surface_main_frame_where_stopped(fid: str, frame: str) -> Surface:
    """Для FrameWhereStopped - кадр где остановились"""
    pad_x_coef = 0.045  # ширины пропорции
    pad_y_coef = 0.04  # высоты 3 линии

    height = int(MAIN_SF_HEIGHT_PX * MENU_LINE_3_H_COEF)
    width = int(height // MAIN_SF_PROPORTION)

    back_sf = Surface((width, height), **SURFACE_ARGS)

    main_sf = Surface((width - width * pad_x_coef * 2, (height - height * pad_y_coef * 2) * 0.97), **SURFACE_ARGS)
    main_sf.set_alpha(100)
    main_sf.fill(Color('gold'))

    img_frame = load_frame(fid, frame)
    main_sf = smoothscale(img_frame.convert_alpha(), (
        width - width * pad_x_coef * 2,
        (height - height * pad_y_coef * 2) * 0.97
    ))

    back_sf.blit(main_sf, (width * pad_x_coef, height * pad_y_coef))
    return back_sf


def surface_dust(texture: Surface, alpha: int) -> Surface:
    """
    Поверхность мерцающей пылинки
    alpha==0 это прозрачный, (0-255)
    """
    dust_sf = smoothscale(texture.convert_alpha(), (DUST_SIZE_PX, DUST_SIZE_PX))
    dust_sf.set_alpha(alpha)
    return dust_sf


def surface_menu_background() -> Surface:
    """Для MenuBackground"""
    return smoothscale(IMG_BG_MENU.convert_alpha(), (SCREEN_WIDTH_PX, SCREEN_HEIGHT_PX))


def surface_text_about_player() -> Surface:
    """Для TextAboutPlayer"""
    return _text_surface_ml_3col(I18N_SF_TEXT_ABOUT_PLAYER.replace('PROJECT_VERSION', PROJECT_VERSION))


def surface_text_about_resources() -> Surface:
    """Для TextAboutResources"""
    return _text_surface_ml_3col(I18N_SF_TEXT_ABOUT_RESOURCES)


def surface_text_about_from_author() -> Surface:
    """Для TextAboutFromAuthor"""
    return _text_surface_ml_3col(I18N_SF_TEXT_ABOUT_FROM_AUTHOR)


def surface_text_selected_films(selected_cnt: int, available_cnt: int) -> Surface:
    """Для TextSelectedFilms"""
    return text_surface(
        FONT_UI_TEXT,
        I18N_SF_TEXT_SELECTED_FILMS.replace('{1}', str(selected_cnt)).replace('{2}', str(available_cnt)),
        '#DC143C',
        '#FFFFFF',
    )


def surface_text_search_found(
        search_text: str, is_search_by_artist: bool, found_cnt: int, selected_cnt: int) -> Surface:
    """Для TextSearchFound"""
    target_name = I18N_SF_TEXT_SEARCH_BY_ARTIST if is_search_by_artist else I18N_SF_TEXT_SEARCH_BY_NAME
    counts = I18N_SF_TEXT_SEARCH_FOUND.replace('{1}', str(found_cnt)).replace('{2}', str(selected_cnt))
    target = f'{target_name} "{search_text}" - ' if search_text else ''
    return text_surface(
        FONT_UI_TEXT,
        f'{target}{counts}',
        '#DC143C',
        '#FFFFFF',
    )
