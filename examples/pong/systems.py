from typing import Callable
from random import uniform, choice

import pygame
from pygame import Surface
from pygame.rect import Rect
from pygame.event import Event
from pygame.display import Info as VideoInfo
from pygame.locals import QUIT, KEYDOWN, KEYUP, K_ESCAPE, K_UP, K_DOWN, K_w, K_s, K_SPACE
from ecs_pattern import System, EntityManager

from components import ComMotion, ComVisible
from entities import Ball, GameStateInfo, Racket, Score, Table, TeamScoredGoalEvent, WaitForBallMoveEvent, Spark
from sprites import ball_sprite, racket_sprite, table_sprite, score_sprite, spark_sprite
from consts import Team, BALL_SIZE, RACKET_WIDTH, RACKET_HEIGHT, RACKET_SPEED, BALL_SPEED_MIN


def set_random_ball_speed(ball: Ball, screen_info: VideoInfo, x_direction: int):
    assert x_direction in (1, -1), 'Wrong direction'
    min_speed = int(BALL_SPEED_MIN * screen_info.current_h)
    ball.speed_x = uniform(min_speed, min_speed * 2) * x_direction
    ball.speed_y = uniform(min_speed, min_speed * 2) * choice((1, -1))


class SysInit(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities

    def start(self):
        screen_info = pygame.display.Info()
        self.entities.init(
            TeamScoredGoalEvent(Team.LEFT),
            Spark(spark_sprite(pygame.display.Info()), 0, 0, 0, 0)
        )
        self.entities.add(
            GameStateInfo(
                play=True,
                pause=False
            ),
            WaitForBallMoveEvent(1000),
            Score(
                sprite=score_sprite(0),
                x=int(screen_info.current_w * 0.25),
                y=int(screen_info.current_h * 0.2),
                team=Team.LEFT,
                score=0
            ),
            Score(
                sprite=score_sprite(0),
                x=int(screen_info.current_w * 0.75),
                y=int(screen_info.current_h * 0.2),
                team=Team.RIGHT,
                score=0
            ),
            Ball(
                sprite=ball_sprite(screen_info),
                x=int(screen_info.current_w * 0.5 - BALL_SIZE * screen_info.current_h / 2),
                y=int(screen_info.current_h * 0.5 - BALL_SIZE * screen_info.current_h / 2),
                speed_x=0, speed_y=0
            ),
            Racket(
                sprite=racket_sprite(screen_info),
                x=0,
                y=int(screen_info.current_h / 2 - screen_info.current_h * RACKET_HEIGHT / 2),
                team=Team.LEFT,
                speed_x=0, speed_y=0
            ),
            Racket(
                sprite=racket_sprite(screen_info),
                x=int(screen_info.current_w - screen_info.current_h * RACKET_WIDTH),
                y=int(screen_info.current_h / 2 - screen_info.current_h * RACKET_HEIGHT / 2),
                team=Team.RIGHT,
                speed_x=0, speed_y=0
            ),
            Table(
                sprite=table_sprite(screen_info),
                x=0,
                y=0
            ),
        )
        print('Ping')

    def stop(self):
        print('Pong')


class SysMovement(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.game_state_info = None

    def start(self):
        self.game_state_info = next(self.entities.get_by_class(GameStateInfo))

    def update(self):
        if self.game_state_info.pause:
            return
        # get entities
        ball = next(self.entities.get_by_class(Ball))
        table = next(self.entities.get_by_class(Table))
        # move
        for movable_entity in self.entities.get_with_component(ComMotion, ComVisible):
            movable_entity.x += movable_entity.speed_x
            movable_entity.y += movable_entity.speed_y
        # ball reflect
        if ball.y < table.y:
            ball.speed_y = -ball.speed_y
        if ball.y > table.sprite.rect.height - ball.sprite.rect.height:
            ball.speed_y = -ball.speed_y
        # racket
        ball_rect = Rect(ball.x, ball.y, ball.sprite.rect.width, ball.sprite.rect.height)
        for racket in self.entities.get_by_class(Racket):
            # hit ball
            if ball_rect.colliderect(Rect(racket.x, racket.y, racket.sprite.rect.width, racket.sprite.rect.height)):
                set_random_ball_speed(ball, pygame.display.Info(), -1 if ball.speed_x > 0 else 1)
                if racket.team == Team.LEFT:
                    ball.x = racket.x + racket.sprite.rect.width + 1
                else:
                    ball.x = racket.x - ball.sprite.rect.width - 1
            # wall border
            if racket.y < table.y:
                racket.y = table.y
            if racket.y > table.sprite.rect.height - racket.sprite.rect.height:
                racket.y = table.sprite.rect.height - racket.sprite.rect.height
        # goal
        if ball.x < table.x or ball.x > table.sprite.rect.width - ball.sprite.rect.width:
            team_scored_goal = Team.RIGHT if ball.x < table.x else Team.LEFT
            self.entities.add(
                TeamScoredGoalEvent(team_scored_goal),
                WaitForBallMoveEvent(1000)
            )
            screen_info = pygame.display.Info()
            min_speed = int(BALL_SPEED_MIN * screen_info.current_h)
            for i in range(40):
                self.entities.add(
                    Spark(
                        sprite=spark_sprite(screen_info),
                        x=ball.x,
                        y=ball.y,
                        speed_x=uniform(min_speed / 3, min_speed * 4) * choice((1, -1)),
                        speed_y=uniform(min_speed / 3, min_speed * 4) * choice((1, -1)),
                    )
                )
            ball.x = int(screen_info.current_w * 0.5 - BALL_SIZE * screen_info.current_h / 2)
            ball.y = int(screen_info.current_h * 0.5 - BALL_SIZE * screen_info.current_h / 2)
            ball.speed_x = 0
            ball.speed_y = 0
        # kill sparks
        table_rect = Rect(table.x, table.y, table.sprite.rect.width, table.sprite.rect.height)
        for spark in self.entities.get_by_class(Spark):
            if not table_rect.colliderect(
                    Rect(spark.x, spark.y, spark.sprite.rect.width, spark.sprite.rect.height)):
                self.entities.delete_buffer_add(spark)
        self.entities.delete_buffer_purge()


class SysGoal(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities

    def update(self):
        team_scored_goal_event: TeamScoredGoalEvent = next(self.entities.get_by_class(TeamScoredGoalEvent), None)
        if team_scored_goal_event:
            score_entity: Score
            for score_entity in self.entities.get_by_class(Score):
                if score_entity.team == team_scored_goal_event.team:
                    score_entity.score += 1
                    score_entity.sprite = score_sprite(score_entity.score)
            self.entities.delete(team_scored_goal_event)


class SysRoundStarter(System):
    def __init__(self, entities: EntityManager, clock: pygame.time.Clock):
        self.entities = entities
        self.clock = clock

    def update(self):
        wait_for_ball_move_event: WaitForBallMoveEvent = next(self.entities.get_by_class(WaitForBallMoveEvent), None)
        if wait_for_ball_move_event:
            wait_for_ball_move_event.wait_ms -= self.clock.get_time()
            if wait_for_ball_move_event.wait_ms <= 0:
                self.entities.delete(wait_for_ball_move_event)
                set_random_ball_speed(next(self.entities.get_by_class(Ball)), pygame.display.Info(), choice((1, -1)))


class SysControl(System):
    def __init__(self, entities: EntityManager, event_getter: Callable[..., list[Event]]):
        self.entities = entities
        self.event_getter = event_getter
        self.move_keys = (K_w, K_s, K_UP, K_DOWN)
        self.event_types = (KEYDOWN, KEYUP, QUIT)  # white list
        self.game_state_info = None
        self.pressed_keys = []

    def start(self):
        self.game_state_info = next(self.entities.get_by_class(GameStateInfo))

    def update(self):
        for event in self.event_getter(self.event_types):
            event_type = event.type
            event_key = getattr(event, 'key', None)

            # quit game
            if (event_type == KEYDOWN and event_key == K_ESCAPE) or event_type == QUIT:
                self.game_state_info.play = False

            # pause
            if event_type == KEYDOWN and event_key == K_SPACE:
                self.game_state_info.pause = not self.game_state_info.pause

            # move rackets
            if event_key in self.move_keys:
                screen_info = pygame.display.Info()
                racket: Racket

                if event_type == KEYDOWN:
                    self.pressed_keys.append(event_key)
                elif event_type == KEYUP:
                    self.pressed_keys.remove(event_key)

                for racket in self.entities.get_by_class(Racket):
                    # left up
                    if event_key == K_w and racket.team == Team.LEFT:
                        if event_type == KEYDOWN:
                            racket.speed_y = int(screen_info.current_h * -RACKET_SPEED)
                        elif event_type == KEYUP and K_s not in self.pressed_keys:
                            racket.speed_y = 0
                    # left down
                    if event_key == K_s and racket.team == Team.LEFT:
                        if event_type == KEYDOWN:
                            racket.speed_y = int(screen_info.current_h * RACKET_SPEED)
                        elif event_type == KEYUP and K_w not in self.pressed_keys:
                            racket.speed_y = 0
                    # right up
                    if event_key == K_UP and racket.team == Team.RIGHT:
                        if event_type == KEYDOWN:
                            racket.speed_y = int(screen_info.current_h * -RACKET_SPEED)
                        elif event_type == KEYUP and K_DOWN not in self.pressed_keys:
                            racket.speed_y = 0
                    # right down
                    if event_key == K_DOWN and racket.team == Team.RIGHT:
                        if event_type == KEYDOWN:
                            racket.speed_y = int(screen_info.current_h * RACKET_SPEED)
                        elif event_type == KEYUP and K_UP not in self.pressed_keys:
                            racket.speed_y = 0


class SysDraw(System):
    def __init__(self, entities: EntityManager, screen: Surface):
        self.entities = entities
        self.screen = screen

    def update(self):
        for visible_entity in self.entities.get_by_class(Table, Score, Ball, Racket, Spark):
            self.screen.blit(visible_entity.sprite.image, (visible_entity.x, visible_entity.y))
