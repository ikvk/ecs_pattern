from typing import Callable, Hashable, List, Tuple

from ecs_pattern import component
from pygame import Mask, Rect, Surface
from pygame.font import Font


@component
class ComLiveTime:
    """Lifetime until the specified second"""
    live_until_time: float  # when monotonic time becomes greater, the object is removed


@component
class ComSurface:
    """Surface (image)"""
    surface: Surface


@component
class Com2dCoord:
    """Two-dimensional coordinates"""
    x: float  # X coordinate on display, 0 on the left
    y: float  # Y coordinate on display, 0 at the top


@component
class ComSpeed:
    """Movement speed"""
    speed_x: float  # pixels per second, *apply FPS correction
    speed_y: float  # pixels per second, *apply FPS correction


@component
class ComAnimationSet:
    """Set of surfaces for animation"""
    frames: Tuple[Surface]


@component
class ComAnimated:
    """Animated object"""
    animation_set: ComAnimationSet  # animation frame set, 0-last frame, len(animation_set)-first frame
    animation_looped: bool  # animation is looped or removed after completion
    animation_frame: int  # current animation frame, the value is SUBTRACTED
    animation_frame_float: float  # for calculating animation_frame switching
    animation_speed: float  # frames per second, *apply FPS correction


@component
class _ComUiElement:
    """Common properties of GUI elements"""
    rect: Rect  # Rect(left, top, width, height), for coarse mouse movement detection
    mask: Mask  # for pixel-perfect collision detection
    scenes: List[Hashable]  # on which logical scenes to display the element
    state: int  # control state, one of CS_SET


@component
class ComUiButton(_ComUiElement):
    """GUI element - button"""
    sf_static: Surface
    sf_hover: Surface
    sf_pressed: Surface
    on_click: Callable = lambda: None


@component
class ComUiInput(_ComUiElement):
    """GUI element - text input field"""
    font: Font
    max_length: int
    sf_static: Surface
    sf_static_empty: Surface  # with placeholder
    sf_active: Surface  # during input
    text: str = ''  # text in the input field
    cursor_char: str = '_'  # character of the blinking input cursor
    on_confirm: Callable = lambda: None  # input confirmation - enter, graphical input on Android
    on_change: Callable = lambda: None  # text change


@component
class ComUiText(_ComUiElement):
    """GUI element - multiline text"""
    sf_text: Surface


@component
class ComUiCheckbox(_ComUiElement):
    """GUI element - checkbox"""
    checked: bool  # main boolean value - whether it is checked
    sf_static_0: Surface
    sf_hover_0: Surface
    sf_pressed_0: Surface
    sf_static_1: Surface
    sf_hover_1: Surface
    sf_pressed_1: Surface
    on_change: Callable = lambda: None  # first checked is changed, then on_change is called


@component
class ComUiScroll(_ComUiElement):
    """GUI element - scroll bar"""
    pointer_rect: Rect  # pointer rectangle
    position_count: int  # number of selectable positions, >= 1
    position_current: int  # selected position, from 0 to position_count-1
    position_future: int  # future position, during slider movement, from 0 to position_count-1
    sf_bar_static: Surface  # base
    sf_pointer_static: Surface  # pointer
    sf_pointer_hover: Surface
    sf_pointer_pressed: Surface
    on_change: Callable = lambda: None
