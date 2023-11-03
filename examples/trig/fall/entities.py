from typing import Tuple, Optional

from ecs_pattern import entity
from numpy import ndarray

from common_tools.components import ComSurface, ComSpeed, Com2dCoord, ComAnimationSet, ComAnimated, ComUiInput, \
    ComUiButton, ComUiText


@entity
class GameData:
    do_play: bool  # Флаг продолжения основного цикла игры
    scene_active: int  # текущая сцена

    do_figure_fast_fall: bool  # Флаг быстрого падения фигуры - для кнопок
    do_figure_fast_fall_until: float  # Быстрое падение фигуры до указанной секунды - для тача и мыши
    do_figure_spawn: bool  # Флаг указывает на необходимость создать фигуру
    do_figure_live_pause_until: float  # пауза жизни фигур до указанной секунды (monotonic)

    score: int  # Количество заработанных очков
    speed: int  # Текущая скорость игры
    pause_cnt: int  # Количество пауз
    figure_current: Tuple[int, int]  # (Индекс фигуры, Индекс варианта фигуры), текущая фигура, для переворота
    figure_next: Tuple[int, int]  # (Индекс фигуры, Индекс варианта фигуры), следующая фигура
    figure_dir: int  # Направление падения фигуры: PLUS_MINUS_ONE
    figure_row: int  # На сколько сдвинута строка фигуры с момента создания, для возможности переворота
    figure_col: int  # На сколько сдвинут столбец фигуры с момента создания, для возможности переворота
    last_move_time: int  # Время последнего передвижения фигуры вниз

    event_score_coord: Optional[Tuple[int, int]]  # x, y активатора начисления случайного кол-ва очков, флаг
    event_score: int  # Количество очков за взятие активатора

    event_no_intersect_coord: Optional[Tuple[int, int]]  # x, y активатора режима падения без препятствий, флаг
    event_no_intersect_now: bool  # Признак включенного режима фигуры - падение без препятствий

    grid_figure_active: ndarray  # Матрица активной фигуры
    grid_static: ndarray  # Матрица со статичными треугольниками
    grid_temp1: ndarray  # Временная матрица 1
    grid_temp2: ndarray  # Временная матрица 2

    grid_rows_for_del: [Tuple[int, int]]  # строки матрицы для предстоящей очистки
    grid_cells_for_del: [Tuple[int, int]]  # ячейки матрицы для предстоящей очистки
    grid_cells_for_del_blocked: [Tuple[int, int]]  # ячейки матрицы для предстоящей очистки, заблокированные


@entity
class TriangleActiveUp(ComSurface):
    """Треугольник для текущей фигуры, вершина вверх"""


@entity
class TriangleActiveDown(ComSurface):
    """Треугольник для текущей фигуры, вершина вниз"""


@entity
class TriangleStaticUp(ComSurface):
    """Треугольник для статичной фигуры, вершина вверх"""


@entity
class TriangleStaticDown(ComSurface):
    """Треугольник для статичной фигуры, вершина вниз"""


@entity
class TriangleGridUp(ComSurface):
    """Треугольник для игровой таблицы, вершина вверх"""


@entity
class TriangleGridDown(ComSurface):
    """Треугольник для игровой таблицы, вершина вниз"""


@entity
class TriangleScoreUp(ComSurface):
    """Треугольник активатора получения очков, вершина вверх"""


@entity
class TriangleScoreDown(ComSurface):
    """Треугольник активатора получения очков, вершина вниз"""


@entity
class TriangleNoIntersectUp(ComSurface):
    """Треугольник активатора режима падения без препятствий, вершина вверх"""


@entity
class TriangleNoIntersectDown(ComSurface):
    """Треугольник активатора режима падения без препятствий, вершина вниз"""


@entity
class InfoArea(Com2dCoord, ComSurface):
    """Поле информации об игре"""


@entity
class PlayArea(Com2dCoord, ComSurface):
    """Игровое поле"""


@entity
class Border(Com2dCoord, ComSurface):
    """Граница инфо поля"""


@entity
class IconNextFigure(ComSurface):
    """Картинка следующей фигуры"""
    pass


@entity
class LabelPause(ComSurface):
    pass


@entity
class LabelGameOver(ComSurface):
    pass


@entity
class TextSpeed(Com2dCoord, ComSurface):
    pass


@entity
class TextScore(Com2dCoord, ComSurface):
    pass


@entity
class SparkDel1AnimationSet(ComAnimationSet):
    """
    Набор искр разной прозрачности для взрыва треугольника при очистке
    0 - прозрачная, 255-не прозрачная
    """

    def __post_init__(self):
        assert len(self.frames) == 256


@entity
class SparkDel2AnimationSet(ComAnimationSet):
    """
    Набор искр разной прозрачности для взрыва треугольника при очистке - вариант для заблокированных
    0 - прозрачная, 255-не прозрачная
    """

    def __post_init__(self):
        assert len(self.frames) == 256


@entity
class Spark(ComSpeed, Com2dCoord, ComAnimated):
    """Затухающая движущаяся искра"""


@entity
class InputPlayerName(ComUiInput):
    """Поле для ввода имени, после окончания игры"""


@entity
class ButtonSaveResult(ComUiButton):
    """Кнопка - Сохранить результат на указанное имя и выйти, после окончания игры"""


@entity
class ButtonResumeGame(ComUiButton):
    """Кнопка - Продолжить игру, при паузе"""


@entity
class ButtonToMainMenu(ComUiButton):
    """Кнопка - Продолжить игру, при паузе"""


@entity
class ButtonExitGame(ComUiButton):
    """Кнопка - Выйти из игры, при паузе"""


@entity
class TextGameResults(ComUiText):
    """Текст - Форма с результатом игры и контролами"""


@entity
class Loading(Com2dCoord, ComSurface):
    """Картинка загрузки"""
