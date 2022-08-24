from ecs_pattern import entity

from components import ComMotion, ComScore, ComTeam, ComVisible, ComWait


@entity
class Ball(ComMotion, ComVisible):
    pass


@entity
class Racket(ComMotion, ComTeam, ComVisible):
    pass


@entity
class Table(ComVisible):
    pass


@entity
class Score(ComScore, ComTeam, ComVisible):
    pass


@entity
class Spark(ComMotion, ComVisible):
    pass


@entity
class TeamScoredGoalEvent(ComTeam):
    pass


@entity
class WaitForBallMoveEvent(ComWait):
    pass


@entity
class GameStateInfo:
    play: bool
    pause: bool
