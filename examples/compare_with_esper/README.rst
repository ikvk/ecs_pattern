.. http://docutils.sourceforge.net/docs/user/rst/quickref.html

⚖️ Compare python ECS libs
========================================================================================================================

Scene with snowflakes and warm shine, implemented on two ECS libs:

1. *snow_esper.py*: pygame + ``esper``
2. *snow_ecs_pattern.py*: pygame + ``ecs_pattern``

🎬 At scene: 50 000 snowflakes with different: transparency, rotation speed, movement speed.

**FPS**:
    | is the same in both variants.
    | ``This proves that literally copying the classic ECS approach in Python is pointless.``

**Memory**:
    | ecs_pattern consumes 96Mb, esper consumes 144Mb.
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
