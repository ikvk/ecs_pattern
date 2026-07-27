from ecs_pattern import entity

from common_tools.components import (
    Com2dCoord,
    ComSurface,
    ComUiButton,
    ComUiScroll,
)


@entity
class PlayerData:
    do_play: bool  # Флаг продолжения основного цикла плеера
    scene_active: int  # текущая сцена
    last_frame_change_start_time: float  # Время старта последнего перелистывания
    last_frame_change_animation_speed_sec: float  # время анимации смены кадров
    last_frame_was_control_event: bool  # были ли события при последнем проходе SysControl.update


@entity
class ButtonFrameNext(ComUiButton):
    """Кнопка - Следующий кадр"""


@entity
class ButtonFramePerv(ComUiButton):
    """Кнопка - Предыдущий кадр"""


@entity
class ButtonFilmNext(ComUiButton):
    """Кнопка - Следующий диафильм"""


@entity
class ButtonFilmPrev(ComUiButton):
    """Кнопка - Предыдущий диафильм"""


@entity
class ButtonHome(ComUiButton):
    """Кнопка - Домой"""


@entity
class ScrollBarFilm(ComUiScroll):
    """Шкала перемотки фильма"""


@entity
class PlayerBackground(Com2dCoord, ComSurface):
    """Общий фон плеера"""


@entity
class FilmFrameCurrent(Com2dCoord, ComSurface):
    """Текущий кадр фильма для отображения"""


@entity
class FilmFramePrev(Com2dCoord, ComSurface):
    """Предыдущий кадр фильма для отображения анимации смены"""
