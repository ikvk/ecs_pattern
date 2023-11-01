import warnings

from pygame import Surface
from pygame.font import Font
from pygame.image import load

from .consts import SCREEN_HEIGHT
from .surface import colored_block_surface


def _load_img(path: str) -> Surface:
    """Загрузить изображение из файла"""
    try:
        return load(path)
    except FileNotFoundError:
        warnings.warn(f'Image not found: {path}')
        return colored_block_surface('#FF00FFff', 100, 100)


# объекты изображений
IMG_SNOWFLAKE = _load_img('_img/snowflake.png')
IMG_SHINE = _load_img('_img/light_shine.png')
IMG_BACKGROUND = _load_img('_img/landscape.jpg')

# объекты шрифтов - Font
FONT_DEFAULT = Font(None, int(SCREEN_HEIGHT / 35))
