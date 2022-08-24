from pygame import Surface, Color
from pygame.sprite import Sprite
from pygame.font import Font
from pygame.display import Info as VideoInfo

from consts import BALL_SIZE, RACKET_WIDTH, RACKET_HEIGHT


class ColoredBlockSprite(Sprite):

    def __init__(self, color: Color, width: int, height: int):
        Sprite.__init__(self)
        self.image = Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()


class SurfaceSprite(Sprite):

    def __init__(self, surface: Surface):
        Sprite.__init__(self)
        self.image = surface
        self.rect = self.image.get_rect()


def ball_sprite(screen_info: VideoInfo) -> Sprite:
    size = int(screen_info.current_h * BALL_SIZE)
    return ColoredBlockSprite(Color('maroon'), size, size)


def racket_sprite(screen_info: VideoInfo) -> Sprite:
    return ColoredBlockSprite(
        Color(240, 240, 240), int(screen_info.current_h * RACKET_WIDTH), int(screen_info.current_h * RACKET_HEIGHT))


def table_sprite(screen_info: VideoInfo) -> Sprite:
    return ColoredBlockSprite(Color('black'), int(screen_info.current_w), int(screen_info.current_h))


def score_sprite(score: int, font_size: int = 80) -> Sprite:
    font = Font(None, font_size)  # None - default font
    font_surface = font.render(str(score), True, Color('steelblue'))
    return SurfaceSprite(font_surface)


def spark_sprite(screen_info: VideoInfo) -> Sprite:
    size = int(screen_info.current_h * BALL_SIZE)
    return ColoredBlockSprite(Color('gold'), size, size)
