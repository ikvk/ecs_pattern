from ecs_pattern import entity
from pygame import Rect
from pygame.mixer import Channel

from common_tools.components import (
    Com2dCoord,
    ComAnimated,
    ComAnimationSet,
    ComSpeed,
    ComSurface,
    ComUiButton,
    ComUiCheckbox,
    ComUiInput,
    ComUiScroll,
    ComUiText,
)


@entity
class MenuData:
    do_menu: bool  # Флаг продолжения основного цикла меню
    scene_active: int  # текущая сцена
    music_channel: Channel  # фоновая музыка меню
    last_dust_spawn_time: float  # Время последнего создания пылинки
    btn_small_rect: Rect  # чтобы не создавать лишний раз
    search_text_last: str  # текст поиска, введенный в последний раз
    search_dust_last_time: float  # время последнего эффекта поиска


@entity
class ButtonAbout(ComUiButton):
    """Кнопка - О программе"""


@entity
class ButtonExit(ComUiButton):
    """Кнопка - Выход"""


@entity
class ButtonSearchOpen(ComUiButton):
    """Кнопка - Поиск - открыть форму"""


@entity
class ButtonRandomFilm(ComUiButton):
    """Кнопка - Случайный диафильм"""


@entity
class ButtonPlay(ComUiButton):
    """Кнопка - Продолжить"""


@entity
class CheckboxSearchByArtist(ComUiCheckbox):
    """Чекбокс - Поиск по художнику"""


@entity
class CheckboxWindowMode(ComUiCheckbox):
    """Чекбокс - Оконный режим"""


@entity
class CheckboxSound(ComUiCheckbox):
    """Чекбокс - Звук"""


@entity
class CheckboxChromaColor(ComUiCheckbox):
    """Чекбокс - Цветность - Цветной"""


@entity
class CheckboxChromaBlackWhite(ComUiCheckbox):
    """Чекбокс - Цветность - Чёрно-белый"""


@entity
class CheckboxCategoryNovellasAndStories(ComUiCheckbox):
    """Чекбокс - Категория - Повести и рассказы"""


@entity
class CheckboxCategoryFairyTales(ComUiCheckbox):
    """Чекбокс - Категория - Сказки"""


@entity
class CheckboxCategoryPoemsAndFables(ComUiCheckbox):
    """Чекбокс - Категория - Стихи и басни"""


@entity
class CheckboxAge0Plus(ComUiCheckbox):
    """Чекбокс - Возраст - 0+"""


@entity
class CheckboxAge6Plus(ComUiCheckbox):
    """Чекбокс - Возраст - 6+"""


@entity
class CheckboxAge12Plus(ComUiCheckbox):
    """Чекбокс - Возраст - 12+"""


@entity
class MenuBackground(Com2dCoord, ComSurface):
    """Общий фон меню"""


@entity
class FrameWhereStopped(Com2dCoord, ComSurface):
    """Кадр фильма, на котором остановились"""


@entity
class FrameBorder(Com2dCoord, ComSurface):
    """Рамка кадра, на котором остановились"""


@entity
class Header(Com2dCoord, ComSurface):
    """Заголовок сцены"""


#     текст - в 3 колонки - о плеере, ресурсы,
#     кнопка домой

@entity
class Dust(ComSpeed, Com2dCoord, ComAnimated):
    """Мерцающая движущаяся пылинка"""


@entity
class DustAnimationSet(ComAnimationSet):
    """
    Кадры анимации пылинки
    0 - прозрачная, 255-не прозрачная
    """

    def __post_init__(self):
        if len(self.frames) != 256:
            raise ValueError


@entity
class TextSelectedFilms(ComUiText):
    """Текст - выбрано Х из У доступных"""


@entity
class TextAboutPlayer(ComUiText):
    """Текст - о плеере"""


@entity
class TextAboutResources(ComUiText):
    """Текст - ресурсы"""


@entity
class TextAboutFromAuthor(ComUiText):
    """Текст - от автора"""


# далее элементы формы поиска


@entity
class ButtonSearchDo(ComUiButton):
    """Кнопка - Поиск - Искать"""


@entity
class ButtonSearchReset(ComUiButton):
    """Кнопка - Поиск - Сброс"""


@entity
class ButtonHome(ComUiButton):
    """Кнопка - Поиск - На главный экран"""


@entity
class ButtonSearchNextPage(ComUiButton):
    """Кнопка - Поиск - Следующая страница поиска"""


@entity
class ButtonSearchPrevPage(ComUiButton):
    """Кнопка - Поиск - Предыдущая страница поиска"""


@entity
class ButtonSearchFilmCard(ComUiButton):
    """Кнопка - Отображение найденного диафильма и переход к нему"""
    fid: str = ''  # id диафильма


@entity
class ScrollBarSearch(ComUiScroll):
    """Шкала перемотки"""


@entity
class InputSearchFilm(ComUiInput):
    """Поле для ввода текста поиска"""


@entity
class TextSearchFound(ComUiText):
    """Текст - найдено Х из У выбранных"""
