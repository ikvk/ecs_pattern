.. http://docutils.sourceforge.net/docs/user/rst/quickref.html

Compare python ECS libs speed
========================================================================================================================

Scene with snowflakes and warm shine, implemented on:

1. ``snow_esper.py``: pygame + esper
2. ``snow_ecs_pattern.py``: pygame + ecs_pattern

At scene: 50 000 snowflakes with different: transparency, rotation speed, movement speed.

FPS is the same in both variants, with any SNOWFLAKE_CNT.

``This proves that literally copying the classic ECS approach in Python is pointless.``

Consumption of other resources is the same.

In my opinion ``ecs_pattern`` is much more pythonic than ``esper``.
