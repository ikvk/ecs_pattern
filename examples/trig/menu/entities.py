from ecs_pattern import entity
from pygame.mixer import Channel

from common_tools.components import ComUiButton, ComUiText, Com2dCoord, ComSurface, ComAnimationSet, \
    ComAnimated


@entity
class MenuData:
    do_menu: bool  # Флаг продолжения основного цикла меню
    scene_active: int  # текущая сцена
    music_channel: Channel  # фоновая музыка меню


@entity
class Background(Com2dCoord, ComSurface):
    """Общий фон меню"""


@entity
class LabelGameName(Com2dCoord, ComSurface):
    """Название игры"""


@entity
class ButtonToMenuRoot(ComUiButton):
    """Кнопка - Переход к главному меню"""


@entity
class ButtonPlay(ComUiButton):
    """Кнопка - старт игры"""


@entity
class ButtonGuide(ComUiButton):
    """Кнопка - Как играть"""


@entity
class ButtonSettings(ComUiButton):
    """Кнопка - Настройки"""


@entity
class ButtonRecords(ComUiButton):
    """Кнопка - Достижения"""


@entity
class ButtonAbout(ComUiButton):
    """Кнопка - Об игре"""


@entity
class ButtonExit(ComUiButton):
    """Кнопка - Выход"""


@entity
class TextGuide(ComUiText):
    """Текст - Как играть"""


@entity
class TextRecords(ComUiText):
    """Текст - Достижения"""


@entity
class TextAbout(ComUiText):
    """Текст - Об игре"""


@entity
class TextSettings(ComUiText):
    """Текст - Настройки"""


@entity
class ButtonGraphicHigh(ComUiButton):
    """Кнопка - Качество графики - высокое"""


@entity
class ButtonGraphicMiddle(ComUiButton):
    """Кнопка - Качество графики - среднее"""


@entity
class ButtonGraphicLow(ComUiButton):
    """Кнопка - Качество графики - низкое"""


@entity
class ButtonSoundNormal(ComUiButton):
    """Кнопка - Включить звук 100%"""


@entity
class ButtonSoundQuiet(ComUiButton):
    """Кнопка - Включить звук 40%"""


@entity
class ButtonSoundDisable(ComUiButton):
    """Кнопка - Выключить звук"""


@entity
class ButtonScreenModeFull(ComUiButton):
    """Кнопка - Включить режим окна - полный экран"""


@entity
class ButtonScreenModeWindow(ComUiButton):
    """Кнопка - Включить режим окна - окно"""


@entity
class ShineLightAnimationSet(ComAnimationSet):
    """Набор кадров анимации сияния света - светлый вариант"""


@entity
class ShineDarkAnimationSet(ComAnimationSet):
    """Набор кадров анимации сияния света - тёмный вариант"""


@entity
class Shine(Com2dCoord, ComAnimated):
    """Анимация - сияние света"""


@entity
class ButtonLanguageRu(ComUiButton):
    """Кнопка - Включить русский язык"""


@entity
class ButtonLanguageEn(ComUiButton):
    """Кнопка - Включить английский язык"""
