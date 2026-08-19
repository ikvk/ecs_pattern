.. http://docutils.sourceforge.net/docs/user/rst/quickref.html

⚖️ Compare python ECS libs: esper and ecs_pattern
========================================================================================================================

Scene with snowflakes and warm shine, implemented on two ECS libs:

1. `snow_esper.py <https://github.com/ikvk/ecs_pattern/blob/master/examples/compare_with_esper/snow_esper.py>`_: pygame + ``esper``
2. `snow_ecs_pattern.py <https://github.com/ikvk/ecs_pattern/blob/master/examples/compare_with_esper/snow_ecs_pattern.py>`_: pygame + ``ecs_pattern``

🎬 At scene: 50 000 snowflakes with different: transparency, rotation speed, movement speed.

**FPS**:
    | is the same in both variants. With any number of snowflakes.
    | ``This proves that literally copying the classic ECS approach in Python (like in esper) is pointless.``

**Memory**:
    | ecs_pattern consumes 96Mb, esper consumes 144Mb. The gap is the same for any number of snowflakes.
    | ``ecs_pattern has a significant advantage due to the use of optimal data structures.``

**CPU**:
    | is the same in both variants = 10%. As expected.

**Code**:
    | ``ecs_pattern has a much simpler interface``

📋 Conclusion:

* ``ecs_pattern`` consumes significantly less memory than ``esper``
* ``ecs_pattern`` ecs_pattern has a much simpler interface than ``esper``
* ``ecs_pattern`` is much more pythonic than ``esper``
* FPS and CPU usage - the same.

🚀 Choose the ``ecs_pattern`` library! ⭐
