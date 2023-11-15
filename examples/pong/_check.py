import time
import pygame

from ecs_pattern import EntityManager

from entities import Ball, GameStateInfo, Racket, Score, Table, TeamScoredGoalEvent, WaitForBallMoveEvent
from sprites import ball_sprite, racket_sprite, table_sprite, score_sprite
from consts import Team, BALL_SIZE, RACKET_WIDTH, RACKET_HEIGHT
from components import ComVisible, ComMotion, ComScore, ComTeam, ComWait

pygame.init()
screen_info = pygame.display.Info()

score_spr = score_sprite(0)
ball_spr = ball_sprite(screen_info)
racket_spr = racket_sprite(screen_info)
table_spr = table_sprite(screen_info)


def show_memory_usage(function):
    """
    if __name__ == '__main__':
        show_memory_usage(leak)
    """
    from memory_profiler import memory_usage
    mem_usage = memory_usage(function, interval=.1)
    print('Maximum memory usage for {}: {} Mb'.format(function.__name__, max(mem_usage)))


def _add_10_entities(entity_manager):
    """
    1_000_000 add
        _entity_map - []
            20.662492752075195 sec
            Maximum memory usage for entity_manager: 1949.73828125 Mb
        _entity_map - deque()
            21.873197555541992 sec
            Maximum memory usage for entity_manager: 1954.2734375 Mb

    100_000 add
        _entity_map - []
            1.790226697921753 sec
            Maximum memory usage for entity_manager: 238.71875 Mb
        _entity_map - deque()
            1.8341341018676758 sec
            Maximum memory usage for entity_manager: 240.05859375 Mb
    """
    entity_manager.add(
        GameStateInfo(play=True, pause=False),
        GameStateInfo(play=False, pause=False),
        TeamScoredGoalEvent(Team.RIGHT),
        WaitForBallMoveEvent(1000),
        Score(
            sprite=score_spr,
            x=int(screen_info.current_w * 0.25),
            y=int(screen_info.current_h * 0.2),
            team=Team.LEFT,
            score=0
        ),
        Score(
            sprite=score_spr,
            x=int(screen_info.current_w * 0.75),
            y=int(screen_info.current_h * 0.2),
            team=Team.RIGHT,
            score=0
        ),
        Ball(
            sprite=ball_spr,
            x=int(screen_info.current_w * 0.5 - BALL_SIZE * screen_info.current_h / 2),
            y=int(screen_info.current_h * 0.5 - BALL_SIZE * screen_info.current_h / 2),
            speed_x=0, speed_y=0
        ),
        Racket(
            sprite=racket_spr,
            x=0,
            y=int(screen_info.current_h / 2 - screen_info.current_h * RACKET_HEIGHT / 2),
            team=Team.LEFT,
            speed_x=0, speed_y=0
        ),
        Racket(
            sprite=racket_spr,
            x=int(screen_info.current_w - screen_info.current_h * RACKET_WIDTH),
            y=int(screen_info.current_h / 2 - screen_info.current_h * RACKET_HEIGHT / 2),
            team=Team.RIGHT,
            speed_x=0, speed_y=0
        ),
        Table(
            sprite=table_spr,
            x=0,
            y=0
        ),
    )


def entity_manager_access():
    """
    _entity_map

    access 20_000 get_with_component
        []
            13.37865400314331 sec
            Maximum memory usage for entity_manager: 52.3203125 Mb
        deque()
            14.869358777999878 sec
            Maximum memory usage for entity_manager: 51.96875 Mb

    access 20_000 get_by_class
        []
            15.288840770721436 sec
            Maximum memory usage for entity_manager: 52.29296875 Mb
        deque()
            17.244649410247803 sec
            Maximum memory usage for entity_manager: 52.38671875 Mb
    """

    entities = EntityManager()

    t = time.time()

    for k in range(1_000):
        _add_10_entities(entities)

    for k in range(20_000):
        for _ in entities.get_with_component(ComVisible, ComMotion, ComScore, ComTeam, ComWait):
            pass
        for _ in entities.get_with_component(ComVisible):
            pass
        for _ in entities.get_with_component(ComMotion):
            pass
        for _ in entities.get_with_component(ComScore):
            pass
        for _ in entities.get_with_component(ComTeam):
            pass
        for _ in entities.get_with_component(ComWait):
            pass

        # * при тесте надо закомментить 1 из частей - get_with_component или get_by_class

        for _ in entities.get_by_class(Ball, GameStateInfo, Racket, Score, Table, TeamScoredGoalEvent,
                                       WaitForBallMoveEvent):
            pass
        for _ in entities.get_by_class(Ball):
            pass
        for _ in entities.get_by_class(GameStateInfo):
            pass
        for _ in entities.get_by_class(Racket):
            pass
        for _ in entities.get_by_class(Score):
            pass
        for _ in entities.get_by_class(Table):
            pass
        for _ in entities.get_by_class(TeamScoredGoalEvent):
            pass
        for _ in entities.get_by_class(WaitForBallMoveEvent):
            pass

    print(time.time() - t, 'sec')


def entity_manager_delete_buffer():
    """
    100_000

    []
        20.23709201812744 sec
        Maximum memory usage for entity_manager_delete_buffer: 249.19140625 Mb
    deque()
        19.756350994110107 sec
        Maximum memory usage for entity_manager_delete_buffer: 248.75390625 Mb

    deque() pop IndexError
        20.462244749069214 sec
        Maximum memory usage for entity_manager_delete_buffer: 249.0703125 Mb

    from queue import Queue, Empty - get_nowait
        24.581512689590454 sec
        Maximum memory usage for entity_manager_delete_buffer: 248.80859375 Mb
    """

    entities = EntityManager()

    t = time.time()

    for i in range(100_000):
        _add_10_entities(entities)

    for ent in entities.get_by_class(Ball, GameStateInfo, Racket, Score, Table, TeamScoredGoalEvent,
                                     WaitForBallMoveEvent):
        entities.delete_buffer_add(ent)
    entities.delete_buffer_purge()

    print(time.time() - t, 'sec')


def entity_dataclass_slots():
    """
    Checking entity dataclass slots

    Dataclass that inherits another dataclass (1 on N super classes):
        on slots=1: contains empty __dict__
        on slots=0: contains full __dict__
    I do not found reason for empty __dict__ in docs
    I suppose that it is enough for save memory in python and can not be better

    component = dataclass
    entity = partial(dataclass, slots=True)
        1_000_000 - Maximum memory usage for entity_dataclass_slots: 1095.3125 Mb
        100_000 - Maximum memory usage for entity_dataclass_slots: 160.890625 Mb

    component = dataclass
    entity = partial(dataclass, slots=False)
        1_000_000 - Maximum memory usage for entity_dataclass_slots: 1940.8984375 Mb
        100_000 - Maximum memory usage for entity_dataclass_slots: 241.96484375 Mb

    component = dataclass
    entity = dataclass
        1_000_000 - Maximum memory usage for entity_dataclass_slots: 1940.67578125 Mb
        100_000 - Maximum memory usage for entity_dataclass_slots: 242.8984375 Mb

    """
    entities = EntityManager()
    for i in range(1_000_000):
        _add_10_entities(entities)


def lib_dataclass_mem():
    """
    8_000_000
        Maximum memory usage for lib_dataclass_mem: 3250.58984375 Mb
    2_000_000
        Maximum memory usage for lib_dataclass_mem: 830.5625 Mb
    200_000
        Maximum memory usage for lib_dataclass_mem: 126.40625 Mb
    """
    from dataclasses import dataclass, field
    cnt = 8_000_000

    @dataclass
    class Class1:
        number: int = 42
        list_of_numbers: list = field(default_factory=list)
        string: str = ''

    data = []
    for i in range(cnt):
        data.append(Class1(i, [1, 2, 3], str(i) * 5))


def lib_attrs_mem():
    """
    8_000_000
        Maximum memory usage for lib_attrs_mem: 2552.12890625 Mb
    2_000_000
        Maximum memory usage for lib_attrs_mem: 643.125 Mb
    200_000
        Maximum memory usage for lib_attrs_mem: 103.33203125 Mb
    """
    from attrs import define, Factory
    cnt = 8_000_000

    @define
    class Class1:
        number: int = 42
        list_of_numbers: list[int] = Factory(list)
        string: str = ''

    data = []
    for i in range(cnt):
        data.append(Class1(i, [1, 2, 3], str(i) * 5))


if __name__ == '__main__':
    # show_memory_usage(entity_manager_access)
    # show_memory_usage(entity_manager_delete_buffer)
    # show_memory_usage(entity_dataclass_slots)
    # show_memory_usage(lib_dataclass_mem)
    # show_memory_usage(lib_attrs_mem)

    pass
