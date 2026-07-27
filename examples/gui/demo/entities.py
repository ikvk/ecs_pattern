from ecs_pattern import entity

from common_tools.components import (
    ComUiButton,
    ComUiCheckbox,
    ComUiInput,
    ComUiScroll,
    ComUiText,
)


@entity
class DemoData:
    do_demo: bool  # Флаг продолжения основного цикла меню
    scene_active: int  # текущая сцена


@entity
class Button1(ComUiButton):
    pass


@entity
class Button2(ComUiButton):
    pass


@entity
class Checkbox1(ComUiCheckbox):
    pass


@entity
class ScrollBar1(ComUiScroll):
    pass


@entity
class Input1(ComUiInput):
    pass


@entity
class Text1(ComUiText):
    pass
