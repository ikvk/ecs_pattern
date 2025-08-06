import configparser
import datetime
import locale
import os
import sys
import warnings

SETTING_GRAPHIC_LOW = 'l'
SETTING_GRAPHIC_MIDDLE = 'm'
SETTING_GRAPHIC_HIGH = 'h'

SETTING_SOUND_NORMAL = 'n'
SETTING_SOUND_QUIET = 'q'
SETTING_SOUND_DISABLED = 'd'

SETTING_SCREEN_MODE_FULL = 'f'
SETTING_SCREEN_MODE_WINDOW = 'w'

SETTING_LANGUAGE_RU = 'ru'
SETTING_LANGUAGE_EN = 'en'


def _clean_player_name(player_name: str) -> str:
    return player_name.replace(',', '_').replace('|', '_')


class SettingsStorage:
    """Интерфейс для хранения настроек игры"""

    _config_section = 'GAME'
    _config_encoding = 'utf8'
    _dt_format = '%Y-%b-%d %H:%M'

    _key_graphic = 'graphic'
    _key_sound = 'sound'
    _key_screen_mode = 'screen_mode'
    _key_language = 'language'
    _key_player_name = 'player_name'
    _key_records = 'records'

    _valid_keys = {
        _key_graphic: (SETTING_GRAPHIC_LOW, SETTING_GRAPHIC_MIDDLE, SETTING_GRAPHIC_HIGH),
        _key_sound: (SETTING_SOUND_NORMAL, SETTING_SOUND_QUIET, SETTING_SOUND_DISABLED),
        _key_screen_mode: (SETTING_SCREEN_MODE_FULL, SETTING_SCREEN_MODE_WINDOW),
        _key_language: (SETTING_LANGUAGE_RU, SETTING_LANGUAGE_EN),
        _key_player_name: None,  # any
        _key_records: None,  # any
    }

    def __init__(self, user_data_dir: str, is_android_: bool):
        # пример: C:\Users\v.kaukin\AppData\Roaming\game.ikvk.trig_fall_pay\trig_fall.ini
        self.config_file_path = os.path.join(user_data_dir, 'trig_fall.ini')
        self.is_android = is_android_

        self.config = configparser.ConfigParser()
        self.config.read(self.config_file_path, encoding=self._config_encoding)
        if self._config_section not in self.config:
            self.config[self._config_section] = {}

        # VK Play
        # GameUILocaleParam=-my_ui_locale_arg=
        # При старте игры будет передано -my_ui_locale_arg=XXXX,
        # где XXXX ru-RU, en-US, de-DE, es-ES, fr-FR, it-IT, pl-PL, tr-TR, zh-CN, ko-KR, ja-JP).
        vk_play_locale_lang_code = \
            next((i.replace('-my_ui_locale_arg=', '') for i in sys.argv if '-my_ui_locale_arg' in i), '')  # works

        locale_lang_code, locale_encoding = locale.getlocale()  # после pyinstaller exe = (None, None)
        locale_lang_code = (locale_lang_code or vk_play_locale_lang_code).lower()
        ru_by_default = 'russia' in locale_lang_code or locale_lang_code in ('ru', 'ru_ru', 'ru-ru')
        self.defaults = {
            self._key_graphic: SETTING_GRAPHIC_MIDDLE if self.is_android else SETTING_GRAPHIC_HIGH,
            self._key_sound: SETTING_SOUND_NORMAL,
            self._key_screen_mode: SETTING_SCREEN_MODE_FULL,  # if self.is_android else SETTING_SCREEN_MODE_WINDOW, *VK
            self._key_language: SETTING_LANGUAGE_RU if ru_by_default else SETTING_LANGUAGE_EN,
            self._key_player_name: 'Player',
            self._key_records: '',
        }
        for key in self._valid_keys.keys():
            if not self._read(key):
                self._write(key, self.defaults[key])

    def _read(self, key: str) -> str:
        res = self.config[self._config_section].get(key, '')
        has_valid_keys = self._valid_keys[key]
        if has_valid_keys and res and res not in self._valid_keys[key]:
            warnings.warn(
                f'SettingsStorage invalid value: "{res}" for key: "{key}" at "{self.config_file_path}" (fixed)',
                stacklevel=2)
            self._write(key, self.defaults[key])
            return self.defaults[key]
        return res

    def _write(self, key: str, value: str):
        has_valid_keys = self._valid_keys[key]
        if has_valid_keys:
            if value not in self._valid_keys[key]:
                raise ValueError
        self.config[self._config_section][key] = value
        with open(self.config_file_path, 'w', encoding=self._config_encoding) as f:
            self.config.write(f)

    @property
    def graphic(self) -> str:
        return self._read(self._key_graphic)

    @graphic.setter
    def graphic(self, value: str):
        self._write(self._key_graphic, value)

    @property
    def sound(self) -> str:
        return self._read(self._key_sound)

    @sound.setter
    def sound(self, value: str):
        self._write(self._key_sound, value)

    @property
    def screen_mode(self) -> str:
        return self._read(self._key_screen_mode)

    @screen_mode.setter
    def screen_mode(self, value: str):
        self._write(self._key_screen_mode, value)

    @property
    def language(self) -> str:
        return self._read(self._key_language)

    @language.setter
    def language(self, value: str):
        self._write(self._key_language, value)

    @property
    def player_name(self) -> str:
        return self._read(self._key_player_name)

    @player_name.setter
    def player_name(self, value: str):
        self._write(self._key_player_name, _clean_player_name(value)[:100])

    @property
    def records(self) -> [[str, str, str], ...]:
        data_str = self._read(self._key_records)
        res = []
        for i in data_str.split('|'):
            line_set = i.split(',')
            if len(line_set) == 3:
                res.append(line_set)
        return res

    def records_add(self, score: int, player_name: str):
        """
        При добавлении сортирует и ограничивает количество
        Формат: "Очки,игрок,время|Очки,игрок,время"
        """
        new_rec = f'{score},{_clean_player_name(player_name)},{datetime.datetime.now().strftime(self._dt_format)}'
        curr_data_str = self._read(self._key_records)
        new_data_str = '|'.join([i for i in [new_rec, curr_data_str] if i])
        max_records = 25
        try:
            record_str_list = sorted(new_data_str.split('|'), key=lambda x: int(x.split(',')[0]), reverse=True)
            self._write(self._key_records, '|'.join(record_str_list[:max_records]))
        except Exception as e:
            warnings.warn(f'error on records_add (fixed): {e}', stacklevel=2)
            self._write(self._key_records, new_rec)

    def records_clean(self):
        self._write(self._key_records, '')
