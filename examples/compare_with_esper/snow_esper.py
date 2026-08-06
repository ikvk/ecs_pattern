import math
import sys
from random import uniform, choice
from typing import Tuple

import pygame
from pygame import DOUBLEBUF, FULLSCREEN, SCALED, SRCALPHA, Color, Surface
from pygame.locals import K_ESCAPE, KEYDOWN, MOUSEBUTTONDOWN, MOUSEMOTION, QUIT
from pygame.time import Clock

import esper

# ── Константы (скопированы один‑в‑один из оригинала) ─────────────────────
pygame.init()
_desktop_size_set = pygame.display.get_desktop_sizes()
_desktop_max_h = max(height for _, height in _desktop_size_set)
_desktop_w, _desktop_h = next((w, h) for w, h in _desktop_size_set if h == _desktop_max_h)
_is_horizontal_desktop = _desktop_h < _desktop_w

_graphics_quality_div = 1
_desktop_w /= _graphics_quality_div
_desktop_h /= _graphics_quality_div

SETTING_SCREEN_IS_FULLSCREEN = False
if SETTING_SCREEN_IS_FULLSCREEN:
    SCREEN_WIDTH = _desktop_w
    SCREEN_HEIGHT = _desktop_h
else:
    SCREEN_HEIGHT = _desktop_h * 0.8
    SCREEN_WIDTH = SCREEN_HEIGHT

SHINE_SIZE = 0.38
SHINE_WARM_SPEED_MUL = 10
SNOWFLAKE_SIZE_FROM = 0.002
SNOWFLAKE_SIZE_TO = 0.03
SNOWFLAKE_SIZE_CNT = 64
SNOWFLAKE_SIZE_STEP = (SNOWFLAKE_SIZE_TO - SNOWFLAKE_SIZE_FROM) / SNOWFLAKE_SIZE_CNT
SNOWFLAKE_CNT = 50_000
SNOWFLAKE_ANIMATION_FRAMES = 360
SNOWFLAKE_ANIMATION_SPEED_MIN = 2.0
SNOWFLAKE_ANIMATION_SPEED_MAX = 40.0
SNOWFLAKE_SPEED_X_RANGE = (-10.0, 10.0)
SNOWFLAKE_SPEED_Y_RANGE = (15.0, 40.0)

FPS_MAX = 60
FPS_SHOW = True
SURFACE_ARGS = dict(flags=SRCALPHA, depth=32)


# ── Вспомогательные функции для графики ────────────────────────────────────
def colored_block_surface(color, width, height):
    surf = Surface((width, height), **SURFACE_ARGS)
    surf.fill(color)
    return surf


def _load_img(path: str) -> Surface:
    try:
        return pygame.image.load(path)
    except FileNotFoundError:
        print(f"Image not found: {path}")
        return colored_block_surface('#FF00FFFF', 100, 100)


IMG_BASE = r'../../examples/snow_day/_img'
IMG_SNOWFLAKE = _load_img(f'{IMG_BASE}/snowflake.png')
IMG_SHINE = _load_img(f'{IMG_BASE}/light_shine.png')
IMG_BACKGROUND = _load_img(f'{IMG_BASE}/landscape.jpg')

FONT_DEFAULT = pygame.font.Font(None, int(SCREEN_HEIGHT / 35))


def blit_rotated(surf: Surface, image: Surface, pos, origin_pos, angle: int, fill_color=(0, 0, 0, 0)):
    image_rect = image.get_rect(topleft=(pos[0] - origin_pos[0], pos[1] - origin_pos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)
    surf.blit(rotated_image, rotated_image_rect)
    pygame.draw.rect(surf, fill_color, (*rotated_image_rect.topleft, *rotated_image.get_size()), 2)


def surface_background() -> Surface:
    return pygame.transform.scale(IMG_BACKGROUND.convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))


def surface_shine() -> Surface:
    return pygame.transform.scale(IMG_SHINE.convert_alpha(),
                                  (SCREEN_HEIGHT * SHINE_SIZE, SCREEN_HEIGHT * SHINE_SIZE))


def surface_snowflake_animation_set(scale_: float, alpha_: int, reverse: bool) -> Tuple[Surface, ...]:
    size = SCREEN_HEIGHT * scale_
    snowflake_sf = pygame.transform.scale(IMG_SNOWFLAKE.convert_alpha(), (size, size))
    frames = []
    for i in range(SNOWFLAKE_ANIMATION_FRAMES):
        angle = int(360 / SNOWFLAKE_ANIMATION_FRAMES) * i
        new_sf = Surface((size, size), **SURFACE_ARGS).convert_alpha()
        req_center = (size / 2, size / 2)
        blit_rotated(new_sf, snowflake_sf, req_center, req_center, angle)
        new_sf.set_alpha(alpha_)
        frames.append(new_sf)
    if reverse:
        frames.reverse()
    return tuple(frames)


# ── Компоненты (чистые классы, без логики) ─────────────────────────────────
class Position:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class Velocity:
    def __init__(self, speed_x: float, speed_y: float):
        self.speed_x = speed_x
        self.speed_y = speed_y


class Renderable:
    """Статическое изображение."""

    def __init__(self, surface: Surface):
        self.surface = surface


class Animation:
    def __init__(self, frames: Tuple[Surface, ...], frame_index: int = 0,
                 frame_float: float = 0.0, speed: float = 1.0, looped: bool = True):
        self.frames = frames
        self.frame_index = frame_index
        self.frame_float = frame_float
        self.speed = speed
        self.looped = looped
        self.frame_w = frames[0].get_width()
        self.frame_h = frames[0].get_height()


class ShineTag:
    """Метка для сущности-сияния."""
    pass


# ── Инициализация сцены (создание сущностей) ──────────────────────────────
def setup():
    """Создаёт все начальные сущности в активном мировом контексте."""
    # подготовка наборов анимации снежинок
    snowflake_animation_set_collection = []
    snowflake_alpha_step = 255 / SNOWFLAKE_SIZE_CNT * 0.99
    for i in range(SNOWFLAKE_SIZE_CNT):
        scale_rate = SNOWFLAKE_SIZE_FROM + i * SNOWFLAKE_SIZE_STEP
        alpha = 255 - int(i * snowflake_alpha_step)
        rev = choice((True, False))
        snowflake_animation_set_collection.append(
            surface_snowflake_animation_set(scale_rate, alpha, rev)
        )

    # снежинки
    for _ in range(SNOWFLAKE_CNT):
        frames = choice(snowflake_animation_set_collection)
        esper.create_entity(
            Position(uniform(0, SCREEN_WIDTH),
                     uniform(0, SCREEN_HEIGHT) - SCREEN_HEIGHT * SNOWFLAKE_SIZE_TO),
            Velocity(uniform(*SNOWFLAKE_SPEED_X_RANGE),
                     uniform(*SNOWFLAKE_SPEED_Y_RANGE)),
            Animation(frames,
                      speed=uniform(SNOWFLAKE_ANIMATION_SPEED_MIN,
                                    SNOWFLAKE_ANIMATION_SPEED_MAX),
                      looped=True)
        )

    # фон
    esper.create_entity(
        Position(0.0, 0.0),
        Renderable(surface_background())
    )

    # сияние (shine)
    esper.create_entity(
        Position(SCREEN_HEIGHT / 2, SCREEN_HEIGHT / 2),
        Renderable(surface_shine()),
        ShineTag()
    )


# ── Процессоры ─────────────────────────────────────────────────────────────
class MovementProcessor(esper.Processor):
    def __init__(self, clock: Clock):
        self.clock = clock
        self.half_shine_size = SCREEN_HEIGHT * SHINE_SIZE / 2

    def process(self):
        now_fps = self.clock.get_fps() or FPS_MAX

        # находим позицию сияния
        shine_pos = None
        for ent, (pos, _) in esper.get_components(Position, ShineTag):
            shine_pos = pos
            break

        for ent, (pos, vel, anim) in esper.get_components(Position, Velocity, Animation):
            pos.x += vel.speed_x / now_fps
            pos.y += vel.speed_y / now_fps

            # возврат наверх
            if pos.y > SCREEN_HEIGHT:
                pos.x = uniform(0, SCREEN_WIDTH)
                pos.y = 0 - anim.frame_h

            # влияние тепла от сияния
            if shine_pos is not None:
                dist_to_shine = math.dist(
                    (pos.x + anim.frame_w, pos.y + anim.frame_h),
                    (shine_pos.x + self.half_shine_size, shine_pos.y + self.half_shine_size)
                )
                if dist_to_shine <= self.half_shine_size:
                    sign = 1 if abs(
                        pos.x + anim.frame_w - (shine_pos.x + self.half_shine_size)) < self.half_shine_size else -1
                    pos.x += vel.speed_x / now_fps * SHINE_WARM_SPEED_MUL * sign / (dist_to_shine * 0.01)


class AnimationProcessor(esper.Processor):
    def __init__(self, clock: Clock):
        self.clock = clock

    def process(self):
        now_fps = self.clock.get_fps() or FPS_MAX
        for ent, anim in esper.get_component(Animation):
            anim.frame_float -= anim.speed / now_fps
            anim.frame_index = math.trunc(anim.frame_float)
            if anim.frame_float < 0:
                if anim.looped:
                    anim.frame_index = len(anim.frames) - 1
                    anim.frame_float = float(anim.frame_index)
                else:
                    esper.delete_entity(ent)


class ControlProcessor(esper.Processor):
    def process(self):
        shine_pos = None
        for ent, (pos, _) in esper.get_components(Position, ShineTag):
            shine_pos = pos
            break

        for event in pygame.event.get():
            if event.type == MOUSEMOTION and shine_pos is not None:
                shine_pos.x = event.pos[0] - SCREEN_HEIGHT * SHINE_SIZE / 2
                shine_pos.y = event.pos[1] - SCREEN_HEIGHT * SHINE_SIZE / 2
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    print('L')
                elif event.button == 3:
                    print('R')
            elif event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                sys.exit()


class RenderProcessor(esper.Processor):
    def __init__(self, display: Surface, clock: Clock):
        self.display = display
        self.clock = clock
        self.fps_color = Color('#1339AC')
        self.fps_pos = (0, SCREEN_HEIGHT * 0.98)

    def process(self):
        # статические изображения
        for ent, (pos, rend) in esper.get_components(Position, Renderable):
            self.display.blit(rend.surface, (pos.x, pos.y))
        # анимированные
        for ent, (pos, anim) in esper.get_components(Position, Animation):
            self.display.blit(anim.frames[anim.frame_index], (pos.x, pos.y))
        # счётчик FPS
        if FPS_SHOW:
            fps_text = FONT_DEFAULT.render(
                f'FPS: {int(self.clock.get_fps())}', True, self.fps_color)
            self.display.blit(fps_text, self.fps_pos)


# ── Точка входа ────────────────────────────────────────────────────────────
def main():
    pygame.display.set_caption('Snow day (esper)')
    display = pygame.display.set_mode(
        size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        flags=(FULLSCREEN | SCALED if SETTING_SCREEN_IS_FULLSCREEN else 0) | DOUBLEBUF,
        depth=SURFACE_ARGS['depth']
    )
    clock = Clock()

    # Создаём сущности в дефолтном мировом контексте
    setup()

    # Добавляем процессоры (порядок добавления = порядок выполнения)
    esper.add_processor(ControlProcessor(), priority=1)
    esper.add_processor(MovementProcessor(clock), priority=2)
    esper.add_processor(AnimationProcessor(clock), priority=3)
    esper.add_processor(RenderProcessor(display, clock), priority=4)

    while True:
        clock.tick_busy_loop(FPS_MAX)
        esper.process()  # вызывает process() у всех процессоров по порядку
        pygame.display.flip()


if __name__ == '__main__':
    main()
