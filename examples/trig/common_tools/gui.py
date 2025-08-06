import time

import pygame
from ecs_pattern import EntityManager
from pygame import Mask, Rect, Surface, Vector2
from pygame.event import Event
from pygame.key import set_text_input_rect, start_text_input, stop_text_input
from pygame.locals import (
    K_BACKSPACE,
    K_KP_ENTER,
    K_RETURN,
    KEYDOWN,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    TEXTINPUT,
)
from pygame.transform import smoothscale

from common_tools.components import ComUiButton, ComUiInput, ComUiText
from common_tools.consts import BS_HOVER, BS_PRESSED, BS_STATIC, BUTTON_WIDTH, IS_ACTIVE, IS_STATIC, SCREEN_WIDTH_PX
from common_tools.resources import FONT_BUTTON, FONT_TEXT_ML, IMG_BUTTON_RECT
from common_tools.surface import colorize_surface, text_surface

_MOUSE_EVENT_SET = (MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION)


def is_point_in_mask(point: Vector2, mask: Mask, obj_rect: Rect) -> bool:
    try:
        return bool(mask.get_at((point[0] - obj_rect.x, point[1] - obj_rect.y)))
    except IndexError:
        return False


def gui_button_attrs(x: int, y: int, text: str, w_scale: float = 1) -> dict:
    """Графическая часть атрибутов для кнопки"""
    bg = IMG_BUTTON_RECT
    button_width = SCREEN_WIDTH_PX * BUTTON_WIDTH * w_scale
    scale_rate = button_width / bg.get_width() / w_scale * 0.75
    button_sf = smoothscale(bg.convert_alpha(), (button_width, bg.get_height() * scale_rate))

    font_sf = text_surface(FONT_BUTTON, text, '#F0F8FF', '#696969', 0.05)
    fw, fh = font_sf.get_size()
    w, h = button_sf.get_size()

    button_sf.blit(font_sf, (w / 2 - fw / 2, h / 2 - fh / 2))

    sf_static = button_sf
    sf_hover = colorize_surface(button_sf, '#FFD700')
    sf_pressed = colorize_surface(button_sf, '#7FFFD4')  # Аквамарин

    return dict(
        rect=Rect(x, y, w, h),
        sf_static=sf_static,
        sf_hover=sf_hover,
        sf_pressed=sf_pressed,
        mask=pygame.mask.from_surface(sf_static),
        state=BS_STATIC,
    )


def draw_button(surface: Surface, scene_active: int, entities: EntityManager):
    """Вывод кнопки на поверхность"""
    for button in entities.get_with_component(ComUiButton):
        if scene_active not in button.scenes:
            continue
        if button.state == BS_STATIC:
            surface.blit(button.sf_static, (button.rect[0], button.rect[1]))
        elif button.state == BS_HOVER:
            surface.blit(button.sf_hover, (button.rect[0], button.rect[1]))
        elif button.state == BS_PRESSED:
            surface.blit(button.sf_pressed, (button.rect[0], button.rect[1]))


def draw_input(surface: Surface, scene_active: int, entities: EntityManager):
    """Вывод поля ввода на поверхность"""
    for input_ in entities.get_with_component(ComUiInput):
        if scene_active not in input_.scenes:
            continue
        left, top, width, height = input_.rect
        if input_.state == IS_STATIC:
            surface.blit(input_.sf_static, (left, top))
        elif input_.state == IS_ACTIVE:
            surface.blit(input_.sf_active, (left, top))
        if input_.state == IS_ACTIVE:
            cursor = '' if divmod(time.time(), 1)[1] > 0.5 else '_'
        else:
            cursor = ''
        text_sf = text_surface(FONT_TEXT_ML, input_.text + cursor, '#2F4F4F', '#FFFF00')
        surface.blit(text_sf, (left + height * 0.38, top + height / 2 - text_sf.get_height() / 2))


def draw_text_ml(surface: Surface, scene_active: int, entities: EntityManager):
    """Вывод текстовой панели на поверхность"""
    for text_ml in entities.get_with_component(ComUiText):
        if scene_active not in text_ml.scenes:
            continue
        surface.blit(text_ml.sf_bg, (text_ml.rect[0], text_ml.rect[1]))
        surface.blit(text_ml.sf_text, (text_ml.rect[0], text_ml.rect[1]))


def control_button(event: Event, event_type: int, scene_active: int, entities: EntityManager) -> bool:
    """
    Управление кнопками
    Возвращает - было ли нажатие (any_button_clicked)
    """
    # мышь
    if event_type in _MOUSE_EVENT_SET:
        for button in entities.get_with_component(ComUiButton):
            if button.state != BS_PRESSED or event_type == MOUSEBUTTONUP:
                button.state = BS_STATIC
        for button in entities.get_with_component(ComUiButton):
            if scene_active in button.scenes and is_point_in_mask(event.pos, button.mask, button.rect):
                # кнопка мыши нажата
                if event_type == MOUSEBUTTONDOWN:
                    button.state = BS_PRESSED
                # кнопка мыши отпущена
                elif event_type == MOUSEBUTTONUP:
                    button.state = BS_HOVER
                    button.on_click(entities, event.pos)
                    stop_text_input()
                    return True
                # движение мыши
                elif event_type == MOUSEMOTION:
                    if button.state != BS_PRESSED:
                        button.state = BS_HOVER
    return False


def control_input_activate(event: Event, event_type: int, scene_active: int, entities: EntityManager) -> bool:
    """
    Управление полями ввода
    Возвращает - была ли активация (any_input_clicked)
    """
    if event_type in _MOUSE_EVENT_SET and event_type == MOUSEBUTTONUP:
        # активация поля
        for input_ in entities.get_with_component(ComUiInput):
            if scene_active in input_.scenes and is_point_in_mask(event.pos, input_.mask, input_.rect):
                set_text_input_rect(input_.rect)
                start_text_input()
                input_.state = IS_ACTIVE
                return True
        # никакое поле на сцене не кликнули - потеря фокуса у всех
        stop_text_input()
        for input_ in entities.get_with_component(ComUiInput):
            input_.state = IS_STATIC
    return False


def control_input_edit(event: Event, event_type: int, event_key: int, scene_active: int, entities: EntityManager):
    """
    Ввод текста в поля ввода
    """
    for input_ in entities.get_with_component(ComUiInput):
        if scene_active in input_.scenes and input_.state == IS_ACTIVE:
            if event_type == TEXTINPUT:
                input_.text = input_.text + event.text
                input_.on_edit(entities, Vector2(0, 0))
            elif event_type == KEYDOWN and event_key == K_BACKSPACE:
                input_.text = input_.text[:-1]
                input_.on_edit(entities, Vector2(0, 0))
            elif event_type == KEYDOWN and event_key in [K_RETURN, K_KP_ENTER]:
                input_.on_confirm(entities, Vector2(0, 0))
