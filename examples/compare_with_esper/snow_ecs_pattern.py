import math
import sys
import os
from random import uniform, choice
from typing import Tuple
from dataclasses import field

import pygame
from pygame import SRCALPHA, DOUBLEBUF, FULLSCREEN, SCALED, Surface, Color
from pygame.time import Clock
from pygame.locals import QUIT, MOUSEBUTTONDOWN, MOUSEMOTION, KEYDOWN, K_ESCAPE

from ecs_pattern import component, entity, EntityManager, SystemManager, System

# ── Инициализация Pygame ───────────────────────────────────────────────────
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'

# ── Константы ──────────────────────────────────────────────────────────────
_desktop_size_set = pygame.display.get_desktop_sizes()
_desktop_max_h = max(height for _, height in _desktop_size_set)
_desktop_w, _desktop_h = next((w, h) for w, h in _desktop_size_set if h == _desktop_max_h)

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


# ── Ресурсы ────────────────────────────────────────────────────────────────
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


# ── Поверхности ────────────────────────────────────────────────────────────
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


# ── Компоненты ─────────────────────────────────────────────────────────────
@component
class ComSurface:
    surface: Surface


@component
class Com2dCoord:
    x: float
    y: float


@component
class ComSpeed:
    speed_x: float
    speed_y: float


@component
class ComAnimationSet:
    frames: Tuple[Surface]
    frame_w: int = field(init=False)
    frame_h: int = field(init=False)

    def __post_init__(self):
        self.frame_w = self.frames[0].get_width()
        self.frame_h = self.frames[0].get_height()


@component
class ComAnimated:
    animation_set: ComAnimationSet
    animation_looped: bool
    animation_frame: int
    animation_frame_float: float
    animation_speed: float


# ── Сущности ───────────────────────────────────────────────────────────────
@entity
class Scene1Info:
    do_play: bool


@entity
class Background(Com2dCoord, ComSurface):
    pass


@entity
class Snowflake(Com2dCoord, ComSpeed, ComAnimated):
    pass


@entity
class Shine(Com2dCoord, ComSurface):
    pass


@entity
class SnowflakeAnimationSet(ComAnimationSet):
    pass


# ── Системы ────────────────────────────────────────────────────────────────
class SysInit(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities

    def start(self):
        snowflake_animation_set_collection = []
        snowflake_alpha_step = 255 / SNOWFLAKE_SIZE_CNT * 0.99
        for i, scale_rate in enumerate(range(SNOWFLAKE_SIZE_CNT)):
            snowflake_animation_set_collection.append(surface_snowflake_animation_set(
                scale_=SNOWFLAKE_SIZE_FROM + scale_rate * SNOWFLAKE_SIZE_STEP,  # исправлено
                alpha_=255 - int(i * snowflake_alpha_step),  # исправлено
                reverse=choice((True, False))
            ))

        for _ in range(SNOWFLAKE_CNT):
            self.entities.add(
                Snowflake(
                    x=uniform(0, SCREEN_WIDTH),
                    y=uniform(0, SCREEN_HEIGHT) - SCREEN_HEIGHT * SNOWFLAKE_SIZE_TO,
                    speed_x=uniform(*SNOWFLAKE_SPEED_X_RANGE),
                    speed_y=uniform(*SNOWFLAKE_SPEED_Y_RANGE),
                    animation_set=SnowflakeAnimationSet(choice(snowflake_animation_set_collection)),
                    animation_looped=True,
                    animation_frame=0,
                    animation_frame_float=0.,
                    animation_speed=uniform(SNOWFLAKE_ANIMATION_SPEED_MIN, SNOWFLAKE_ANIMATION_SPEED_MAX),
                ),
            )

        self.entities.add(
            Scene1Info(do_play=True),
            Background(surface_background(), x=0.0, y=0.0),
            Shine(surface_shine(), x=SCREEN_HEIGHT / 2, y=SCREEN_HEIGHT / 2),
        )


class SysLive(System):
    def __init__(self, entities: EntityManager, clock: Clock):
        self.entities = entities
        self.clock = clock
        self.half_shine_size = SCREEN_HEIGHT * SHINE_SIZE / 2
        self.shine = None

    def start(self):
        self.shine = next(self.entities.get_by_class(Shine))

    def update(self):
        now_fps = self.clock.get_fps() or FPS_MAX

        # Движение
        for speed_obj in self.entities.get_with_component(ComSpeed):
            speed_obj.x += speed_obj.speed_x / now_fps
            speed_obj.y += speed_obj.speed_y / now_fps
            if speed_obj.y > SCREEN_HEIGHT:
                speed_obj.x = uniform(0, SCREEN_WIDTH)
                speed_obj.y = 0 - speed_obj.animation_set.frame_h
            dist_to_shine = math.dist(
                (speed_obj.x + speed_obj.animation_set.frame_w, speed_obj.y + speed_obj.animation_set.frame_h),
                (self.shine.x + self.half_shine_size, self.shine.y + self.half_shine_size)
            )
            if dist_to_shine <= self.half_shine_size:
                sign = 1 if abs(
                    speed_obj.x + speed_obj.animation_set.frame_w - (self.shine.x + self.half_shine_size)
                ) < self.half_shine_size else -1
                speed_obj.x += speed_obj.speed_x / now_fps * SHINE_WARM_SPEED_MUL * sign / (dist_to_shine * 0.01)

        # Анимация
        for ani_obj in self.entities.get_with_component(ComAnimated):
            ani_obj.animation_frame_float -= ani_obj.animation_speed / now_fps
            ani_obj.animation_frame = math.trunc(ani_obj.animation_frame_float)
            if ani_obj.animation_frame_float < 0:
                if ani_obj.animation_looped:
                    ani_obj.animation_frame = len(ani_obj.animation_set.frames) - 1
                    ani_obj.animation_frame_float = float(ani_obj.animation_frame)
                else:
                    self.entities.delete_buffer_add(ani_obj)

        self.entities.delete_buffer_purge()


class SysControl(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities

    def update(self):
        for event in pygame.event.get():
            if event.type == MOUSEMOTION:
                shine_obj = next(self.entities.get_by_class(Shine))
                shine_obj.x = event.pos[0] - SCREEN_HEIGHT * SHINE_SIZE / 2
                shine_obj.y = event.pos[1] - SCREEN_HEIGHT * SHINE_SIZE / 2
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    print('L')
                elif event.button == 3:
                    print('R')
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                sys.exit()


class SysDraw(System):
    def __init__(self, entities: EntityManager, display: Surface, clock: Clock):
        self.entities = entities
        self.display = display
        self.clock = clock
        self._fps_pos = (0, SCREEN_HEIGHT * 0.98)
        self._fps_color = Color('#1339AC')

    def update(self):
        # Статические
        for sf_w_pos in self.entities.get_with_component(Com2dCoord, ComSurface):
            self.display.blit(sf_w_pos.surface, (sf_w_pos.x, sf_w_pos.y))
        # Анимированные
        for ani_w_pos in self.entities.get_with_component(Com2dCoord, ComAnimated):
            self.display.blit(ani_w_pos.animation_set.frames[ani_w_pos.animation_frame],
                              (ani_w_pos.x, ani_w_pos.y))
        # FPS
        if FPS_SHOW:
            self.display.blit(
                FONT_DEFAULT.render(f'FPS: {int(self.clock.get_fps())}', True, self._fps_color),
                self._fps_pos
            )


# ── Основной цикл ─────────────────────────────────────────────────────────
def main():
    pygame.display.set_caption('Snow day (ecs_pattern single)')
    display = pygame.display.set_mode(
        size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        flags=(FULLSCREEN | SCALED if SETTING_SCREEN_IS_FULLSCREEN else 0) | DOUBLEBUF,
        depth=SURFACE_ARGS['depth']
    )
    clock = Clock()

    entities = EntityManager()
    system_manager = SystemManager([
        SysInit(entities),
        SysControl(entities),
        SysLive(entities, clock),
        SysDraw(entities, display, clock),
    ])
    system_manager.start_systems()

    info: Scene1Info = next(entities.get_by_class(Scene1Info))

    while info.do_play:
        clock.tick_busy_loop(FPS_MAX)
        system_manager.update_systems()
        pygame.display.flip()

    system_manager.stop_systems()


if __name__ == '__main__':
    main()
