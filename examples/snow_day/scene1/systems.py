import math
from sys import exit  # *for windows
from typing import Callable
from random import choice, uniform

import pygame
from pygame import Surface, Color
from pygame.math import Vector2
from pygame.event import Event
from pygame.locals import QUIT, MOUSEBUTTONDOWN, MOUSEMOTION, KEYDOWN, K_ESCAPE
from ecs_pattern import System, EntityManager

from common_tools.consts import SCREEN_WIDTH, SCREEN_HEIGHT, SHINE_SIZE, SNOWFLAKE_SIZE_FROM, \
    SNOWFLAKE_SIZE_TO, SNOWFLAKE_SIZE_CNT, FPS_MAX, SNOWFLAKE_SIZE_STEP, SNOWFLAKE_CNT, \
    SNOWFLAKE_ANIMATION_SPEED_MAX, SNOWFLAKE_ANIMATION_SPEED_MIN, \
    SNOWFLAKE_SPEED_X_RANGE, SNOWFLAKE_SPEED_Y_RANGE, FPS_SHOW, SHINE_WARM_SPEED_MUL
from common_tools.components import ComAnimated, ComSpeed, Com2dCoord, ComSurface
from common_tools.resources import FONT_DEFAULT
from .entities import Scene1Info, Background, Snowflake, Shine, SnowflakeAnimationSet
from .surfaces import surface_background, surface_snowflake_animation_set, surface_shine


def on_click_lmb(entities: EntityManager, pointer_pos: Vector2):  # noqa
    print('L')


def on_click_rmb(entities: EntityManager, pointer_pos: Vector2):  # noqa
    print('R')


class SysInit(System):

    def __init__(self, entities: EntityManager):
        self.entities = entities

    def start(self):
        snowflake_animation_set_collection = []
        snowflake_alpha_step = 255 / SNOWFLAKE_SIZE_CNT * 0.99
        for i, scale_rate in enumerate(range(SNOWFLAKE_SIZE_CNT)):
            snowflake_animation_set_collection.append(surface_snowflake_animation_set(
                snowflake_scale=SNOWFLAKE_SIZE_FROM + scale_rate * SNOWFLAKE_SIZE_STEP,
                snowflake_alpha=255 - int(i * snowflake_alpha_step),
                reverse=choice((True, False))
            ))

        for i in range(SNOWFLAKE_CNT):
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
            Scene1Info(
                do_play=True,
            ),
            Background(
                surface_background(), x=0.0, y=0.0
            ),
            Shine(
                surface_shine(), x=SCREEN_HEIGHT / 2, y=SCREEN_HEIGHT / 2
            ),
        )


class SysLive(System):

    def __init__(self, entities: EntityManager, clock: pygame.time.Clock):
        self.entities = entities
        self.clock = clock
        self.half_shine_size = SCREEN_HEIGHT * SHINE_SIZE / 2
        self.shine = None

    def start(self):
        self.shine = next(self.entities.get_by_class(Shine))

    def update(self):
        # движение
        now_fps = self.clock.get_fps() or FPS_MAX
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
                speed_obj.x += speed_obj.speed_x / now_fps * SHINE_WARM_SPEED_MUL * (
                    1 if abs(
                        speed_obj.x + speed_obj.animation_set.frame_w - self.shine.x + self.half_shine_size
                    ) < self.half_shine_size else -1
                ) / (dist_to_shine * 0.01)

        # анимация
        for ani_obj in self.entities.get_with_component(ComAnimated):
            ani_obj.animation_frame_float -= ani_obj.animation_speed / now_fps
            ani_obj.animation_frame = ani_obj.animation_frame_float.__trunc__()  # быстрее int()
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
        self.event_getter: Callable[..., list[Event]] = pygame.event.get

    def update(self):
        for event in self.event_getter():
            event_type = event.type
            event_key = getattr(event, 'key', None)

            if event_type == MOUSEMOTION:
                shine_obj = next(self.entities.get_by_class(Shine))
                shine_obj.x = event.pos[0] - SCREEN_HEIGHT * SHINE_SIZE / 2
                shine_obj.y = event.pos[1] - SCREEN_HEIGHT * SHINE_SIZE / 2
            if event_type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    on_click_lmb(self.entities, event.pos)
                if event.button == 3:
                    on_click_rmb(self.entities, event.pos)

            # выйти из игры
            if event_type == QUIT or event_type == KEYDOWN and event_key == K_ESCAPE:
                exit()


class SysDraw(System):

    def __init__(self, entities: EntityManager, display: Surface, clock: pygame.time.Clock):
        self.entities = entities
        self.display = display
        self.clock = clock

    def update(self):
        # static
        for sf_w_pos in self.entities.get_with_component(Com2dCoord, ComSurface):
            self.display.blit(sf_w_pos.surface, (sf_w_pos.x, sf_w_pos.y))
        # animated
        for ani_w_pos in self.entities.get_with_component(Com2dCoord, ComAnimated):
            self.display.blit(ani_w_pos.animation_set.frames[ani_w_pos.animation_frame], (ani_w_pos.x, ani_w_pos.y))
        # fps
        if FPS_SHOW:
            self.display.blit(
                FONT_DEFAULT.render(f'FPS: {int(self.clock.get_fps())}', True, Color('#1339AC')),
                (0, SCREEN_HEIGHT * 0.98)
            )
