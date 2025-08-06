import os
import sys
from functools import cache
from io import BytesIO


def pyinstaller_path_fix(path: str) -> str:
    """PyInstaller creates a temp folder and stores it path in _MEIPASS environment variable"""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, path)


def bytes_buffer_instead_path(path: str) -> BytesIO:
    """
    some problems with pygame on kivy, you can't load a file directly in pygame
    https://stackoverflow.com/questions/75843421/
    """
    with open(pyinstaller_path_fix(path), 'rb') as f:
        return BytesIO(f.read())


def is_android():
    return 'P4A_BOOTSTRAP' in os.environ or 'ANDROID_ARGUMENT' in os.environ


@cache
def get_user_data_dir(package_name: str) -> str:
    """
    Путь к каталогу в файловой системе пользователей,
    который приложение может использовать для хранения дополнительных данных.
    """
    if is_android():
        from jnius import autoclass, cast  # noqa *renamed
        PythonActivity = autoclass('org.kivy.android.PythonActivity')  # noqa
        context = cast('android.content.Context', PythonActivity.mActivity)
        file_p = cast('java.io.File', context.getFilesDir())
        data_dir = file_p.getAbsolutePath()
    elif sys.platform == 'win32':
        data_dir = os.path.join(os.environ['APPDATA'], package_name)  # C:\Users\v.kaukin\AppData\Roaming\
    else:  # 'linux' and other
        data_dir = os.environ.get('XDG_CONFIG_HOME', '~/.config')
        data_dir = os.path.expanduser(os.path.join(data_dir, package_name))
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    return data_dir
