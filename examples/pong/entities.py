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


@entity
class Ball1(ComMotion, ComVisible): pass


@entity
class Ball2(ComMotion, ComVisible): pass


@entity
class Ball3(ComMotion, ComVisible): pass


@entity
class Ball4(ComMotion, ComVisible): pass


@entity
class Ball5(ComMotion, ComVisible): pass


@entity
class Ball6(ComMotion, ComVisible): pass


@entity
class Ball7(ComMotion, ComVisible): pass


@entity
class Ball8(ComMotion, ComVisible): pass


@entity
class Ball9(ComMotion, ComVisible): pass


@entity
class Ball10(ComMotion, ComVisible): pass


@entity
class Ball11(ComMotion, ComVisible): pass


@entity
class Ball12(ComMotion, ComVisible): pass


@entity
class Ball13(ComMotion, ComVisible): pass


@entity
class Ball14(ComMotion, ComVisible): pass


@entity
class Ball15(ComMotion, ComVisible): pass


@entity
class Ball16(ComMotion, ComVisible): pass


@entity
class Ball17(ComMotion, ComVisible): pass


@entity
class Ball18(ComMotion, ComVisible): pass


@entity
class Ball19(ComMotion, ComVisible): pass


@entity
class Ball20(ComMotion, ComVisible): pass


@entity
class Ball21(ComMotion, ComVisible): pass


@entity
class Ball22(ComMotion, ComVisible): pass


@entity
class Ball23(ComMotion, ComVisible): pass


@entity
class Ball24(ComMotion, ComVisible): pass


@entity
class Ball25(ComMotion, ComVisible): pass


@entity
class Ball26(ComMotion, ComVisible): pass


@entity
class Ball27(ComMotion, ComVisible): pass


@entity
class Ball28(ComMotion, ComVisible): pass


@entity
class Ball29(ComMotion, ComVisible): pass


@entity
class Ball30(ComMotion, ComVisible): pass
