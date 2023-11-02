from ecs_pattern import entity

from common_tools.components import ComSurface, ComSpeed, Com2dCoord, ComAnimationSet, ComAnimated


@entity
class Scene1Info:
    do_play: bool  # Флаг продолжения основного цикла игры


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
