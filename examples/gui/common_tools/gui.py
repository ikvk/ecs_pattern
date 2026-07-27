from time import time
from typing import Optional, Tuple

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
from pygame.transform import rotate, smoothscale

from common_tools.components import ComUiButton, ComUiCheckbox, ComUiInput, ComUiScroll, ComUiText
from common_tools.consts import MAIN_SF_HEIGHT_PX, MAIN_SF_WIDTH_PX
from common_tools.resources import (
    FONT_UI_BUTTON,
    FONT_UI_CHECKBOX,
    FONT_UI_INPUT,
    IMG_ICON_FLAG_0,
    IMG_ICON_FLAG_1,
    IMG_UI_BUTTON,
    IMG_UI_BUTTON_SMALL,
    IMG_UI_CHECKBOX,
    IMG_UI_CIRCLE,
    IMG_UI_HEAD,
    IMG_UI_INPUT,
)
from common_tools.surface import colorize_surface, shine_surface, text_surface

# mouse pointer events
MOUSE_EVENT_SET = (MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION)

# event.button buttons of MOUSEBUTTONDOWN pointer event we react to (scroll interfered)
# 1 - left mouse button
# 2 - middle button (wheel)
# 3 - right mouse button
# 4 - scroll wheel up
# 5 - scroll wheel down
# 6 - scroll wheel left (on some mice/OS)
# 7 - scroll wheel right (on some mice/OS)
MOUSE_EVENT_BTN_SET = (1, 2, 3)

# relative to MAIN_SF_WIDTH_PX
_BUTTON_WIDTH_BIG = 0.35  # base width of rectangular buttons
_BUTTON_WIDTH_SMALL = 0.11  # base width of square buttons
_CHECKBOX_WIDTH = 0.3  # base width of checkboxes
_INPUT_WIDTH = 0.28  # base width of inputs

_CONTROL_COLOR_HOVER = '#ffe076'
_CONTROL_COLOR_PRESSED = '#a9ffde'  # Aquamarine
_CONTROL_TEXT_COLOR_MAIN = '#333333'
_CONTROL_TEXT_COLOR_SHADOW = '#F0F0F0'

# Mouse or finger pointer events, Pointer Action
PA_SWIPE_LEFT = 1
PA_SWIPE_RIGHT = 2
PA_SWIPE_UP = 3
PA_SWIPE_DOWN = 4
PA_TAP = 5
PA_NAMES = {
    PA_SWIPE_LEFT: 'PA_SWIPE_LEFT',
    PA_SWIPE_RIGHT: 'PA_SWIPE_RIGHT',
    PA_SWIPE_UP: 'PA_SWIPE_UP',
    PA_SWIPE_DOWN: 'PA_SWIPE_DOWN',
    PA_TAP: 'PA_TAP',
}

# Control states, relative to mouse pointer or finger clicks
CS_STATIC = 1  # pointer outside control bounds
CS_HOVER = 2  # pointer over control
CS_PRESSED = 3  # pointer was pressed over control but not released yet, even if moved outside
CS_INPUT = 4  # input mode, e.g. input field
CS_SET = {CS_STATIC, CS_HOVER, CS_PRESSED, CS_INPUT}


def _is_point_in_mask(point: Vector2, mask: Mask, obj_rect: Rect) -> bool:
    try:
        return bool(mask.get_at((point[0] - obj_rect.x, point[1] - obj_rect.y)))
    except IndexError:
        return False


def make_attrs_button(x: int, y: int, icon: Surface, text: Optional[str] = None) -> dict:
    """
    Build graphical attributes for ComUiButton.
    rel_w and rel_h are set relative to MAIN_SF.
    If text is not specified, this is a square button variant.
    Remaining to fill:
        scenes
        on_click
    """
    small = not bool(text)
    # background
    bg = IMG_UI_BUTTON_SMALL if small else IMG_UI_BUTTON
    scale = 0.65
    scaled_w = MAIN_SF_WIDTH_PX * (_BUTTON_WIDTH_SMALL if small else _BUTTON_WIDTH_BIG) * scale
    scaled_h = bg.get_height() * (0.8 if small else 0.8) * scale
    button_sf = smoothscale(bg.convert_alpha(), (scaled_w, scaled_h))
    w, h = button_sf.get_size()

    # icon
    icon_w = icon_h = h * 0.88
    icon_sf = smoothscale(icon.convert_alpha(), (icon_w, icon_h))
    button_sf.blit(icon_sf, (
        (h - icon_h) / 2 + icon_h * (0.09 if small else 0.04),
        (h - icon_h) / 2
    ))

    # text
    if not small:
        font_sf = text_surface(FONT_UI_BUTTON, text, _CONTROL_TEXT_COLOR_MAIN, _CONTROL_TEXT_COLOR_SHADOW)
        font_w, font_h = font_sf.get_size()
        button_sf.blit(font_sf, (icon_h * 1.4, h / 2 - font_h / 2))

    # surfaces
    sf_static = button_sf
    sf_hover = colorize_surface(button_sf, _CONTROL_COLOR_HOVER)
    sf_pressed = colorize_surface(button_sf, _CONTROL_COLOR_PRESSED)

    return dict(
        state=CS_STATIC,
        rect=Rect(x, y, w, h),
        mask=pygame.mask.from_surface(sf_static),
        sf_static=sf_static,
        sf_hover=sf_hover,
        sf_pressed=sf_pressed,
    )


def make_attrs_checkbox(x: int, y: int, text: str, *, icon1: Surface = None, icon0: Surface = None,
                        scale_w=None, scale_h=None) -> dict:
    """
    Build graphical attributes for ComUiCheckbox.
    Remaining to fill:
        scenes
        checked
        on_change
    """
    scale_w = (scale_w if scale_w else 1)
    scale_h = (scale_h if scale_h else 1) * 0.62

    # background
    bg = IMG_UI_CHECKBOX
    scaled_w = MAIN_SF_WIDTH_PX * _CHECKBOX_WIDTH * scale_w
    scaled_h = bg.get_height() * scaled_w / bg.get_width() * scale_h
    checkbox_sf = smoothscale(bg.convert_alpha(), (scaled_w, scaled_h))
    w, h = checkbox_sf.get_size()

    # flag
    flag_bg = icon1 or IMG_ICON_FLAG_1
    flag_bg_0 = icon0 or IMG_ICON_FLAG_0
    flag_w = flag_h = h * scale_w
    flag_sf = smoothscale(flag_bg.convert_alpha(), (flag_w, flag_h))
    flag_sf_0 = smoothscale(flag_bg_0.convert_alpha(), (flag_w, flag_h))

    # text
    font_sf = text_surface(FONT_UI_CHECKBOX, text, _CONTROL_TEXT_COLOR_MAIN, _CONTROL_TEXT_COLOR_SHADOW)
    font_w, font_h = font_sf.get_size()
    checkbox_sf.blit(font_sf, (scaled_w * 0.33, h / 2 - font_h / 2))

    # surfaces
    flag_left, flag_top = flag_w * 0.28, (h - flag_h) / 2 * 1.15
    sf_static_0 = checkbox_sf
    sf_hover_0 = colorize_surface(checkbox_sf, _CONTROL_COLOR_HOVER)
    sf_pressed_0 = colorize_surface(checkbox_sf, _CONTROL_COLOR_PRESSED)
    sf_static_1 = sf_static_0.copy()
    sf_hover_1 = sf_hover_0.copy()
    sf_pressed_1 = sf_pressed_0.copy()

    sf_static_1.blit(flag_sf, (flag_left, flag_top))
    sf_hover_1.blit(flag_sf, (flag_left, flag_top))
    sf_pressed_1.blit(flag_sf, (flag_left, flag_top + flag_h * 0.05))

    sf_static_0.blit(flag_sf_0, (flag_left, flag_top))
    sf_hover_0.blit(flag_sf_0, (flag_left, flag_top))
    sf_pressed_0.blit(flag_sf_0, (flag_left, flag_top + flag_h * 0.05))

    return dict(
        state=CS_STATIC,
        rect=Rect(x, y, w, h),
        mask=pygame.mask.from_surface(checkbox_sf),
        sf_static_0=sf_static_0,
        sf_hover_0=sf_hover_0,
        sf_pressed_0=sf_pressed_0,
        sf_static_1=sf_static_1,
        sf_hover_1=sf_hover_1,
        sf_pressed_1=sf_pressed_1,
    )


def make_attrs_scroll(x: int, y: int, height: int = None) -> dict:
    """
    Build graphical attributes for ComUiScroll.
    Remaining to fill:
        scenes
        position_count
        position_current
        position_future
        on_change
    """
    # background
    bg = IMG_UI_HEAD
    scroll_sf = rotate(bg.convert_alpha(), 90)
    w = scroll_sf.get_width() * 0.38
    h = height or scroll_sf.get_height() * 0.9
    scroll_sf = smoothscale(scroll_sf, (w, h))

    # pointer
    pointer_bg = IMG_UI_CIRCLE
    pointer_w = w * 0.62
    pointer_h = pointer_w
    pointer_sf = smoothscale(pointer_bg.convert_alpha(), (pointer_w, pointer_h))

    sf_bar_static = scroll_sf
    sf_pointer_static = pointer_sf
    sf_pointer_hover = colorize_surface(pointer_sf, _CONTROL_COLOR_HOVER)
    sf_pointer_pressed = colorize_surface(pointer_sf, _CONTROL_COLOR_PRESSED)

    return dict(
        state=CS_STATIC,
        rect=Rect(x, y, w, h),
        pointer_rect=sf_pointer_static.get_rect(),
        mask=pygame.mask.from_surface(scroll_sf),
        sf_bar_static=sf_bar_static,
        sf_pointer_static=sf_pointer_static,
        sf_pointer_hover=sf_pointer_hover,
        sf_pointer_pressed=sf_pointer_pressed,
    )


def make_attrs_input(x: int, y: int, placeholder: str) -> dict:
    """
    Build graphical attributes for ComUiInput.
    Remaining to fill:
        scenes
        max_length
        text
        on_confirm
        on_change
    """
    # background
    bg = IMG_UI_INPUT
    scaled_w = MAIN_SF_WIDTH_PX * _INPUT_WIDTH
    scaled_h = bg.get_height() * scaled_w / bg.get_width() * 1.15
    input_sf = smoothscale(bg.convert_alpha(), (scaled_w, scaled_h))
    w, h = input_sf.get_size()
    sf_static = shine_surface(input_sf, '#FFD70005', int(FONT_UI_INPUT.get_linesize() * 0.3), 10)
    sf_active = shine_surface(input_sf, '#7FFFD4FF', int(FONT_UI_INPUT.get_linesize() * 0.3), 10)
    sf_static_empty = sf_static.copy()

    # text on static empty field
    font_ph_sf = text_surface(FONT_UI_INPUT, placeholder, '#CCCCCC')
    font_ph_w, font_ph_h = font_ph_sf.get_size()
    sf_static_empty.blit(font_ph_sf, (FONT_UI_INPUT.get_linesize() * 1.38, h / 2 - font_ph_h / 2 + h * 0.12))

    return dict(
        state=CS_STATIC,
        rect=Rect(x, y, w, h),
        mask=pygame.mask.from_surface(input_sf),
        font=FONT_UI_INPUT,
        sf_static=sf_static,
        sf_static_empty=sf_static_empty,
        sf_active=sf_active,
    )


def make_attrs_text(x: int, y: int, sf: Surface) -> dict:
    """
    Build graphical attributes for ComUiText.
    Remaining to fill:
        scenes
    """
    w, h = sf.get_size()
    return dict(
        state=CS_STATIC,
        rect=Rect(x, y, w, h),
        mask=pygame.mask.from_surface(sf),
        sf_text=sf,
    )


def draw_button(surface: Surface, scene_active: int, entities: EntityManager):
    """Draw button on surface"""
    for button in entities.get_with_component(ComUiButton):
        if scene_active not in button.scenes:
            continue
        if button.state == CS_STATIC:
            surface.blit(button.sf_static, (button.rect[0], button.rect[1]))
        elif button.state == CS_HOVER:
            surface.blit(button.sf_hover, (button.rect[0], button.rect[1]))
        elif button.state == CS_PRESSED:
            surface.blit(button.sf_pressed, (button.rect[0], button.rect[1]))


def draw_input(surface: Surface, scene_active: int, entities: EntityManager):
    """Draw input field on surface"""
    for input_ in entities.get_with_component(ComUiInput):
        if scene_active not in input_.scenes:
            continue
        left, top, width, height = input_.rect
        # surface
        if input_.state == CS_STATIC:
            surface.blit(input_.sf_static if input_.text else input_.sf_static_empty, (left, top))
        elif input_.state == CS_INPUT:
            surface.blit(input_.sf_active, (left, top))
        # input cursor
        if input_.state == CS_INPUT:
            cursor_now = '' if divmod(time(), 1)[1] > 0.5 else input_.cursor_char
        else:
            cursor_now = ''
        text_sf = text_surface(FONT_UI_INPUT, input_.text + cursor_now, '#4169E1')
        surface.blit(text_sf, (left + FONT_UI_INPUT.get_linesize() * 1.38,
                               top + height / 2 - text_sf.get_height() / 2 + height * 0.12))


def draw_checkbox(surface: Surface, scene_active: int, entities: EntityManager):
    """Draw checkbox on surface"""
    for checkbox in entities.get_with_component(ComUiCheckbox):
        if scene_active not in checkbox.scenes:
            continue
        if checkbox.checked:
            if checkbox.state == CS_STATIC:
                surface.blit(checkbox.sf_static_1, (checkbox.rect[0], checkbox.rect[1]))
            elif checkbox.state == CS_HOVER:
                surface.blit(checkbox.sf_hover_1, (checkbox.rect[0], checkbox.rect[1]))
            elif checkbox.state == CS_PRESSED:
                surface.blit(checkbox.sf_pressed_1, (checkbox.rect[0], checkbox.rect[1]))
        else:
            if checkbox.state == CS_STATIC:
                surface.blit(checkbox.sf_static_0, (checkbox.rect[0], checkbox.rect[1]))
            elif checkbox.state == CS_HOVER:
                surface.blit(checkbox.sf_hover_0, (checkbox.rect[0], checkbox.rect[1]))
            elif checkbox.state == CS_PRESSED:
                surface.blit(checkbox.sf_pressed_0, (checkbox.rect[0], checkbox.rect[1]))


def draw_text(surface: Surface, scene_active: int, entities: EntityManager):
    """Draw text panel on surface"""
    for text in entities.get_with_component(ComUiText):
        if scene_active not in text.scenes:
            continue
        surface.blit(text.sf_text, (text.rect[0], text.rect[1]))


def draw_scroll(surface: Surface, scene_active: int, entities: EntityManager):
    """Draw scroll on surface"""
    for scroll in entities.get_with_component(ComUiScroll):
        if scene_active not in scroll.scenes:
            continue
        surface.blit(scroll.sf_bar_static, (scroll.rect[0], scroll.rect[1]))

        pointer_x = scroll.rect[0] + scroll.rect[2] / 2 - scroll.pointer_rect[2] / 2
        pointer_move_range = scroll.rect[3] - scroll.pointer_rect[3]
        pointer_y_step = pointer_move_range / ((scroll.position_count - 1) or 1)
        if scroll.state in (CS_STATIC, CS_HOVER):
            pointer_y = scroll.rect[1] + pointer_y_step * scroll.position_current
        elif scroll.state == CS_PRESSED:
            pointer_y = scroll.rect[1] + pointer_y_step * scroll.position_future
        else:
            raise ValueError(f'scroll wrong state: {scroll.state}')

        if scroll.state == CS_STATIC:
            surface.blit(scroll.sf_pointer_static, (pointer_x, pointer_y))
        elif scroll.state == CS_HOVER:
            surface.blit(scroll.sf_pointer_hover, (pointer_x, pointer_y))
        elif scroll.state == CS_PRESSED:
            surface.blit(scroll.sf_pointer_pressed, (pointer_x, pointer_y))


def control_button(event: Event, event_type: int, scene_active: int, entities: EntityManager) -> bool:
    """
    Control buttons
    Returns - whether a click occurred (any_button_clicked)
    If True returned, the control processing chain should be terminated:
        if control_button(...):
            continue
        control_input_activate()
        ...
    """
    # mouse
    if event_type in MOUSE_EVENT_SET:
        for button in entities.get_with_component(ComUiButton):
            # all buttons state becomes static when mouse button released
            if button.state != CS_PRESSED or (event_type == MOUSEBUTTONUP and event.button in MOUSE_EVENT_BTN_SET):
                button.state = CS_STATIC
        for button in entities.get_with_component(ComUiButton):
            # scene active and pointer over mask
            if scene_active in button.scenes and _is_point_in_mask(event.pos, button.mask, button.rect):
                # mouse button pressed
                if event_type == MOUSEBUTTONDOWN and event.button in MOUSE_EVENT_BTN_SET:
                    button.state = CS_PRESSED
                # mouse button released
                elif event_type == MOUSEBUTTONUP and event.button in MOUSE_EVENT_BTN_SET:
                    button.state = CS_STATIC
                    button.on_click(button, entities, event.pos)
                    stop_text_input()
                    return True
                # mouse movement
                elif event_type == MOUSEMOTION:
                    if button.state != CS_PRESSED:
                        button.state = CS_HOVER
    return False


def control_checkbox(event: Event, event_type: int, scene_active: int, entities: EntityManager) -> bool:
    """
    Control checkboxes
    Returns - whether a click occurred (any_checkbox_clicked)
    If True returned, the control processing chain should be terminated:
        if control_checkbox(...):
            continue
        control_input_activate()
        ...
    """
    # mouse
    if event_type in MOUSE_EVENT_SET:
        for checkbox in entities.get_with_component(ComUiCheckbox):
            # all checkboxes state becomes static when mouse button released
            if checkbox.state != CS_PRESSED or (event_type == MOUSEBUTTONUP and event.button in MOUSE_EVENT_BTN_SET):
                checkbox.state = CS_STATIC
        for checkbox in entities.get_with_component(ComUiCheckbox):
            # scene active and pointer over mask
            if scene_active in checkbox.scenes and _is_point_in_mask(event.pos, checkbox.mask, checkbox.rect):
                # mouse button pressed
                if event_type == MOUSEBUTTONDOWN and event.button in MOUSE_EVENT_BTN_SET:
                    checkbox.state = CS_PRESSED
                # mouse button released
                elif event_type == MOUSEBUTTONUP and event.button in MOUSE_EVENT_BTN_SET:
                    checkbox.state = CS_HOVER
                    checkbox.checked = not checkbox.checked
                    checkbox.on_change(checkbox, entities, event.pos)
                    stop_text_input()
                    return True
                # mouse movement
                elif event_type == MOUSEMOTION:
                    if checkbox.state != CS_PRESSED:
                        checkbox.state = CS_HOVER
    return False


def control_scroll(event: Event, event_type: int, scene_active: int, entities: EntityManager) -> bool:
    """
    Control scrolls.
    Returns - whether a click occurred (any_scroll_clicked)
    If True returned, the control processing chain should be terminated:
        if control_scroll(...):
            continue
        control_input_activate()
        ...
    """
    # mouse
    if event_type in MOUSE_EVENT_SET:
        for scroll in entities.get_with_component(ComUiScroll):
            # work with scroll if scene active
            if scene_active not in scroll.scenes:
                continue

            # mouse wheel scrolling (designed for exactly 1 scroll per scene)
            if event_type == MOUSEBUTTONDOWN and event.button not in MOUSE_EVENT_BTN_SET:
                if event.button == 4:
                    # mouse wheel scroll up
                    new_pos = scroll.position_current - 1 if scroll.position_current > 0 else 0
                    scroll.position_current = scroll.position_future = new_pos
                    scroll.state = CS_STATIC
                    scroll.on_change(scroll, entities, event.pos)
                    return True
                elif event.button == 5:
                    # mouse wheel scroll down
                    new_pos = scroll.position_current + 1 \
                        if scroll.position_current < scroll.position_count - 1 else scroll.position_count - 1
                    scroll.position_current = scroll.position_future = new_pos
                    scroll.state = CS_STATIC
                    scroll.on_change(scroll, entities, event.pos)
                    return True

            # pointer over background mask
            if _is_point_in_mask(event.pos, scroll.mask, scroll.rect):
                # mouse button pressed
                if event_type == MOUSEBUTTONDOWN and event.button in MOUSE_EVENT_BTN_SET:
                    scroll.state = CS_PRESSED
                # mouse movement
                elif event_type == MOUSEMOTION:
                    if scroll.state != CS_PRESSED:
                        scroll.state = CS_HOVER
            # pointer not over mask
            else:
                if scroll.state != CS_PRESSED and scroll.state != CS_STATIC:
                    scroll.state = CS_STATIC

            # dragging pointer with mouse
            if scroll.state == CS_PRESSED:
                # calculate position_future
                if (event_type == MOUSEBUTTONDOWN and event.button in MOUSE_EVENT_BTN_SET) \
                        or event_type == MOUSEMOTION:
                    # scroll.rect.top - top edge of active area
                    # scroll.rect.height - height of active area
                    # scroll.position_count - total number of positions
                    mouse_y = event.pos[1]
                    if mouse_y < scroll.rect.top:
                        # pointer above first scroll point
                        scroll.position_future = 0
                    elif mouse_y > scroll.rect.bottom:
                        # pointer below last scroll point
                        scroll.position_future = scroll.position_count - 1
                    else:
                        # calculate pointer position
                        if scroll.position_count <= 1:
                            scroll.position_future = 0
                        # Normalize mouse position relative to active area
                        relative_position = (mouse_y - scroll.rect.top) / scroll.rect.height
                        # Clamp value between 0 and 1
                        relative_position = max(0, min(1, relative_position))
                        # Convert to position index
                        scroll.position_future = int(relative_position * scroll.position_count)
                # mouse button released
                if event_type == MOUSEBUTTONUP and event.button in MOUSE_EVENT_BTN_SET:
                    scroll.position_current = scroll.position_future
                    scroll.state = CS_STATIC
                    scroll.on_change(scroll, entities, event.pos)
                    stop_text_input()
                    return True

    return False


def control_input_activate(event: Event, event_type: int, scene_active: int, entities: EntityManager) -> bool:
    """
    Control input fields
    Returns - whether activation occurred (any_input_clicked)
    """
    if event_type == MOUSEBUTTONUP and event.button in MOUSE_EVENT_BTN_SET:
        # activate field
        for input_ in entities.get_with_component(ComUiInput):
            if scene_active in input_.scenes and _is_point_in_mask(event.pos, input_.mask, input_.rect):
                set_text_input_rect(input_.rect)
                start_text_input()
                input_.state = CS_INPUT
                return True
        # no field on scene clicked - lose focus for all
        stop_text_input()
        for input_ in entities.get_with_component(ComUiInput):
            input_.state = CS_STATIC
    return False


def control_input_edit(event: Event, event_type: int, event_key: int, scene_active: int, entities: EntityManager):
    """
    Text input into input fields
    """
    for input_ in entities.get_with_component(ComUiInput):
        if scene_active in input_.scenes and input_.state == CS_INPUT:
            # character input
            if event_type == TEXTINPUT:
                if len(input_.text) < input_.max_length:
                    input_.text = input_.text + event.text
                    input_.on_change(input_, entities, Vector2(0, 0))
            # Backspace input
            elif event_type == KEYDOWN and event_key == K_BACKSPACE:
                input_.text = input_.text[:-1]
                input_.on_change(input_, entities, Vector2(0, 0))
            # confirm input
            elif event_type == KEYDOWN and event_key in [K_RETURN, K_KP_ENTER]:
                input_.on_confirm(input_, entities, Vector2(0, 0))


class PointerEventGetter:
    """Object for getting mouse or finger pointer events, possible events in PA_NAMES"""

    def __init__(self):
        self._last_pointer_pos_down: Tuple[int, int] = (0, 0)  # remembered press position of mouse or finger
        self._last_pointer_pos_up: Tuple[int, int] = (0, 0)  # remembered release position of mouse or finger
        self._pointer_is_pressed = False  # pointer is pressed
        self._pointer_action = None  # current pointer event (mouse or finger)
        self.switch_dir_accuracy = MAIN_SF_HEIGHT_PX * 0.03  # threshold to distinguish tap from swipe

    def get_pointer_action(self, event: Event) -> Optional[int]:
        event_type = event.type
        # get pointer events (mouse or finger)
        self._pointer_action = None
        if event_type == MOUSEBUTTONDOWN and event.button in MOUSE_EVENT_BTN_SET:
            # mouse button pressed
            self._last_pointer_pos_down = event.pos
            self._pointer_is_pressed = True
        if event_type == MOUSEBUTTONUP and event.button in MOUSE_EVENT_BTN_SET:
            # mouse button released
            self._last_pointer_pos_up = event.pos
            self._pointer_is_pressed = False
            dx = self._last_pointer_pos_up[0] - self._last_pointer_pos_down[0]
            dy = self._last_pointer_pos_up[1] - self._last_pointer_pos_down[1]
            if abs(dx) < self.switch_dir_accuracy and abs(dy) < self.switch_dir_accuracy:
                self._pointer_action = PA_TAP
            elif abs(dy) > abs(dx):
                self._pointer_action = PA_SWIPE_UP if dy < 0 else PA_SWIPE_DOWN
            else:
                self._pointer_action = PA_SWIPE_LEFT if dx < 0 else PA_SWIPE_RIGHT
        return self._pointer_action
