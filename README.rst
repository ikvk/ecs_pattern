.. http://docutils.sourceforge.net/docs/user/rst/quickref.html

========================================================================================================================
ecs_pattern 🚀
========================================================================================================================

Implementation of the ECS pattern (Entity Component System) for creating games.

Make a game instead of architecture for a game.

`Документация на Русском <https://github.com/ikvk/ecs_pattern/blob/master/_docs/README_RUS.rst#ecs_pattern->`_.

.. image:: https://img.shields.io/pypi/dm/ecs_pattern.svg?style=social

===============  ====================================================================================
Python version   3.3+
License          Apache-2.0
PyPI             https://pypi.python.org/pypi/ecs_pattern/
Dependencies     dataclasses before 3.7, typing before 3.5
Repo mirror      https://gitflic.ru/project/ikvk/ecs-pattern
===============  ====================================================================================

.. contents::

Intro
========================================================================================================================
| ECS - Entity-Component-System - it is an architectural pattern created for game development.

It is great for describing a dynamic virtual world.

Basic principles of ECS:

* Composition over inheritance
* Data separated from logic (Data Oriented Design)

| *Component* - Property with object data
| *Entity* - Container for properties
| *System* - Data processing logic
| *EntityManager* - Entity database
| *SystemManager* - Container for systems

Installation
========================================================================================================================
::

    $ pip install ecs-pattern

Guide
========================================================================================================================

.. code-block:: python

    from ecs_pattern import component, entity, EntityManager, System, SystemManager

* Describe components - component
* Describe entities based on components - entity
* Distribute the responsibility of processing entities by systems - System
* Store entities in entity manager - EntityManager
* Manage your systems with SystemManager

Component
------------------------------------------------------------------------------------------------------------------------
    | Property with object data. Contains only data, no logic.

    | Use the ecs_pattern.component decorator to create components.

    | Technically this is python dataclass.

    | Use components as mixins for entities.

    .. code-block:: python

        @component
        class ComPosition:
            x: int = 0
            y: int = 0

        @component
        class ComPerson:
            name: str
            health: int

Entity
------------------------------------------------------------------------------------------------------------------------
    | Container for properties. Consists of components only.

    | It is forbidden to add attributes to an entity dynamically.

    | Use the ecs_pattern.entity decorator to create entities.

    | Technically this is python dataclass with slots=True.

    | Use EntityManager to store entities.

    .. code-block:: python

        @entity
        class Player(ComPosition, ComPerson):
            pass

        @entity
        class Ball(ComPosition):
            pass

System
------------------------------------------------------------------------------------------------------------------------
    | Entity processing logic.

    | Does not contain data about entities and components.

    | Use the ecs_pattern.System abstract class to create concrete systems:

    | *system.start* - Initialize the system. It is called once before the main system update cycle.

    | *system.update* - Update the system status. Called in the main loop.

    | *system.stop* - Stops the system. It is called once after the completion of the main loop.

    | Use SystemManager to manage systems.

    .. code-block:: python

        class SysInit(System):
            def __init__(self, entities: EntityManager):
                self.entities = entities

            def start(self):
                self.entities.init(
                    TeamScoredGoalEvent(Team.LEFT),
                    Spark(spark_sprite(pygame.display.Info()), 0, 0, 0, 0)
                )
                self.entities.add(
                    GameStateInfo(play=True, pause=False),
                    WaitForBallMoveEvent(1000),
                )

        class SysGravitation(System):
            def __init__(self, entities: EntityManager):
                self.entities = entities

            def update(self):
                for entity_with_pos in self.entities.get_with_component(ComPosition):
                    if entity_with_pos.y > 0:
                        entity_with_pos.y -= 1

EntityManager
------------------------------------------------------------------------------------------------------------------------
    | Container for entities.

    | Use class ecs_pattern.EntityManager for creating an entity manager.

    | Time complexity of get_by_class and get_with_component - like a dict

    | *entities.add* - Add entities.

    | *entities.delete* - Delete entities.

    | *entities.delete_buffer_add* - Save entities to the delete buffer to delete later.

    | *entities.delete_buffer_purge* - Delete all entities in the deletion buffer and clear the buffer.

    | *entities.init* - Let manager know about entities. KeyError are raising on access to unknown entities.

    | *entities.get_by_class* - Get all entities of the specified classes. Respects the order of entities.

    | *entities.get_with_component* - Get all entities with the specified components.

    .. code-block:: python

        entities = EntityManager()
        entities.add(
            Player('Ivan', 20, 1, 2),
            Player('Vladimir', 30, 3, 4),
            Ball(0, 7)
        )
        for entity_with_pos in entities.get_with_component(ComPosition):
            print(entity_with_pos.x, entity_with_pos.y)
        for player_entity in entities.get_by_class(Player):
            print(player_entity.name)
            entities.delete_buffer_add(player_entity)
        entities.delete_buffer_purge()
        entities.delete(*tuple(entities.get_by_class(Ball)))  # one line del

SystemManager
------------------------------------------------------------------------------------------------------------------------
    | Container for systems.

    | Works with systems in a given order.

    | Use the ecs_pattern.SystemManager class to manage systems.

    | *system_manager.start_systems* - Initialize systems. Call once before the main systems update cycle.

    | *system_manager.update_systems* - Update systems status. Call in the main loop.

    | *system_manager.stop_systems* - Stop systems. Call once after the main loop completes.

    .. code-block:: python

        entities = EntityManager()
        entities.add(
            Player('Ivan', 20, 1, 2),
            Player('Vladimir', 30, 3, 4),
            Ball(0, 7)
        )
        system_manager = SystemManager([
            SysPersonHealthRegeneration(entities),
            SysGravitation(entities)
        ])
        system_manager.start_systems()
        while play:
            system_manager.update_systems()
            clock.tick(24)  # *pygame clock
        system_manager.stop_systems()

Examples
========================================================================================================================
* `Pong <https://github.com/ikvk/ecs_pattern/tree/master/examples/pong#pong---classic-game>`_: game - pygame + ecs_pattern
* `Snow day <https://github.com/ikvk/ecs_pattern/tree/master/examples/snow_day#snow-day---scene>`_: scene - pygame + ecs_pattern
* `Trig fall <https://github.com/ikvk/ecs_pattern/tree/master/examples/trig#trig-fall---game>`_: commercial game - pygame + ecs_pattern + numpy

Advantages
========================================================================================================================
* Memory efficient - Component and Entity use dataclass
* Convenient search for objects - by entity class and by entity components
* Flexibility - loose coupling in the code allows you to quickly expand the project
* Modularity - the code is easy to test, analyze performance, and reuse
* Execution control - systems work strictly one after another
* Following the principles of the pattern helps to write quality code
* Convenient to parallelize processing
* Compact implementation

Difficulties
========================================================================================================================
* It can take a lot of practice to learn how to cook ECS properly
* Data is available from anywhere - hard to find errors

Newbie mistakes
========================================================================================================================
* Inheritance of components, entities, systems
* Ignoring the principles of ECS, such as storing data in the system
* Raising ECS to the absolute, no one cancels the OOP
* Adaptation of the existing project code under ECS "as is"
* Use of recursive or reactive logic in systems
* Using EntityManager.delete in get_by_class, get_with_component loops

Good Practices
========================================================================================================================
* Use "Singleton" components with data and flags
* Minimize component change locations
* Do not create methods in components and entities
* Divide the project into scenes, a scene can be considered a cycle for the SystemManager with its EntityManager
* Use packages to separate scenes

Project tree example:
::

    /common_tools
        __init__.py
        resources.py
        i18n.py
        gui.py
        consts.py
        components.py
        math.py
    /menu_scene
        __init__.py
        entities.py
        main_loop.py
        surfaces.py
        systems.py
    /game_scene
        __init__.py
        entities.py
        main_loop.py
        surfaces.py
        systems.py
    main.py

Releases
========================================================================================================================

History of important changes: `release_notes.rst <https://github.com/ikvk/ecs_pattern/blob/master/_docs/release_notes.rst>`_

Help the project
========================================================================================================================
* Found a bug or have a suggestion - issue / merge request 🎯
* There is nothing to help this project with - help another open project that you are using ✋
* Nowhere to put the money - spend it on family, friends, loved ones or people around you 💰
* Star the project ⭐
