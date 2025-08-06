"""
Строки с переводом
"""
import gettext

from common_tools.compatibility import pyinstaller_path_fix
from common_tools.consts import SETTINGS_STORAGE
from common_tools.settings import (
    SETTING_GRAPHIC_HIGH,
    SETTING_GRAPHIC_LOW,
    SETTING_GRAPHIC_MIDDLE,
    SETTING_LANGUAGE_EN,
    SETTING_LANGUAGE_RU,
    SETTING_SCREEN_MODE_FULL,
    SETTING_SCREEN_MODE_WINDOW,
    SETTING_SOUND_DISABLED,
    SETTING_SOUND_NORMAL,
    SETTING_SOUND_QUIET,
)

i18n_domain_name = 'trig_fall'  # для локализации
localedir = pyinstaller_path_fix('common_tools/locale')
gettext.install(i18n_domain_name, localedir=localedir)  # install _() function globally into the built-in namespace
lang = gettext.translation(i18n_domain_name, localedir=localedir, languages=[SETTINGS_STORAGE.language], fallback=True)
lang.install()
_ = lang.gettext

I18N_SF_TEXT_RECORDS = _(': Records\n\n')

I18N_SF_TEXT_FREE_VERSION = _(
    'This is a free version of the game with limitations:\n'
    '1. Records are not displayed at this page, example entry:\n'
    '§ 1208 • Name • 2023-JAN-28 16:45\n'
    '2. Yellow triangles appear less frequently.\n'
    '3. After reaching speed 5 in the game, points are not displayed.\n'
    '\n'
    'You can buy the full version of the game in the same store.\n'
    '\n'
    'If this game sells well, I will add the ability to publish achievements online.\n'
)

I18N_SF_TEXT_ABOUT = _(
    ': About\n'
    '\n'
    'Version:\n'
    '• GAME_VERSION\n'
    '\n'
    'Author and developer:\n'
    '• Vladimir Kaukin, KaukinVK@ya.ru\n'
    '\n'
    'Special thanks:\n'
    '• Python language devs\n'
    '• Site: freesound.org\n'
    '• Lib devs: pygame, numpy, python-for-android\n'
    '\n'
    'Fonts:\n'
    '• Devinne Swash: Dieter Steffmann\n'
    '• Faster One: Eduardo Tunni\n'
    '• Alice: Cyreal, Alexei Vanyashin, Gayaneh Bagdasaryan, Ksenia Erulevich\n'
    '\n'
    'Game available at android and windows. Use search.'  # VK play запрещает упоминать платформы размещения приложений
)

I18N_SF_TEXT_GUIDE = _(
    ': Guide\n\n'
    'Figures from the triangles alternately fall down, reflecting off the side walls.\n'
    'A filled line of triangles clears a pair of lines - even and odd, points are awarded for each triangle.\n'
    'Game speed gradually increases when you score points.\n'
    'The goal of the game is to score as many points as possible.\n'
    'Yellow triangle - add random scores.\n'
    'Violet triangle - current figure passes through walls and stops on rotate.\n'
    '\n'
    'MOVE LEFT - Left key, swipe left\n'
    'MOVE RIGHT - Right key, swipe right\n'
    'ROTATE - Up key, swipe up\n'
    'SPEED UP - Down key, swipe down\n'
    'CHANGE DIR - Shift, tap\n'
    'PAUSE - Spacebar, android back\n'
)

I18N_SF_TEXT_SETTINGS = _(
    ': Settings\n\n'
    'Graphic quality: GRAPHIC_CAPTION\n\n\n\n\n'
    'Screen mode: SCREEN_MODE_CAPTION\n\n\n\n\n'
    'Sound: SOUND_CAPTION\n\n\n\n\n'
    'Language: LANGUAGE_CAPTION\n\n\n\n\n'
    '*Restart the game to apply graphic settings\n'
)

I18N_SETTING_GRAPHIC_LOW = _('Low')
I18N_SETTING_GRAPHIC_MIDDLE = _('Middle')
I18N_SETTING_GRAPHIC_HIGH = _('High')
I18N_SETTING_SOUND_DISABLED = _('Disabled')
I18N_SETTING_SOUND_QUIET = _('Quiet')
I18N_SETTING_SOUND_NORMAL = _('Normal')
I18N_SETTING_SCREEN_MODE_FULL = _('Full screen')
I18N_SETTING_SCREEN_MODE_WINDOW = _('Window')
I18N_SETTING_LANGUAGE_RU = _('Русский')
I18N_SETTING_LANGUAGE_EN = _('English')

I18N_BUTTON_TO_MENU_ROOT = _('Main menu')

# словари _CAPTION чтобы избежать кросс референс settings-consts
SETTING_GRAPHIC_CAPTION = {
    SETTING_GRAPHIC_LOW: I18N_SETTING_GRAPHIC_LOW,
    SETTING_GRAPHIC_MIDDLE: I18N_SETTING_GRAPHIC_MIDDLE,
    SETTING_GRAPHIC_HIGH: I18N_SETTING_GRAPHIC_HIGH,
}
SETTING_SOUND_CAPTION = {
    SETTING_SOUND_DISABLED: I18N_SETTING_SOUND_DISABLED,
    SETTING_SOUND_QUIET: I18N_SETTING_SOUND_QUIET,
    SETTING_SOUND_NORMAL: I18N_SETTING_SOUND_NORMAL,
}
SETTING_SCREEN_MODE_CAPTION = {
    SETTING_SCREEN_MODE_FULL: I18N_SETTING_SCREEN_MODE_FULL,
    SETTING_SCREEN_MODE_WINDOW: I18N_SETTING_SCREEN_MODE_WINDOW,
}
SETTING_LANGUAGE_CAPTION = {
    SETTING_LANGUAGE_RU: I18N_SETTING_LANGUAGE_RU,
    SETTING_LANGUAGE_EN: I18N_SETTING_LANGUAGE_EN,
}

I18N_FALL_SAVE_RESULT = _('Save and exit')
I18N_FALL_RESUME_GAME = _('Resume game')
I18N_FALL_TO_MAIN_MENU = _('To main menu')
I18N_FALL_EXIT_GAME = _('Exit game')

I18N_SF_TEXT_GAME_RESULTS = _(
    ' Game over, your result:\n'
    ' SCORE points\n\n'
    ' Player name:\n\n\n\n\n\n\n\n'
)

# Translators: здесь земля будет заменена на \n
I18N_START_GAME_GREETINGS = _(
    """Time for triangular fun!_And triangular problems!
The main rule of the game is that_triangles are always right!
Welcome to the triangular world!
Welcome to the kingdom of triangles!
Here, triangles make the rules!
Catch the rhythm.
Catch the triangular luck!
We triangles are very fond of rows.
No squares,_everything is serious here!
No cubes, just triangles.
Beware of the Bermuda triangle!
Perfectionism will come in handy now!
Win with the power of order!
Immerse yourself_in the world of triangles!
Let's go!
It's getting hot!
Just fill the lines with triangles!
It's time for records.
Your hands are_making history today!
Tip of the day: use triangles!
Become the architect_of the triangular world.
Let's get started!
Triangles are in action.
Triangles are waiting,_show class!
The triangles are calling you!
Triangles are like people,_only triangular.
Triangles on the march!_Collect the rows!
The triangles are already falling,_act decisively!
Triangles: A square is too easy!
Triangular rock-n-roll!
The corners are sharp,_don't get hurt!
Form flawless rows, dominate!
Hey, catch a figure!""")
