.. http://docutils.sourceforge.net/docs/user/rst/quickref.html

========================================================================================================================
ecs_pattern 🚀
========================================================================================================================

Реализация шаблона ECS (Entity Component System) для создания игр.

Делайте игру вместо архитектуры для игры.

`Documentation in English <https://github.com/ikvk/ecs_pattern/blob/master/README.rst>`_.

.. image:: https://img.shields.io/pypi/dm/ecs_pattern.svg?style=social

===============  ==========================================
Python version   3.3+
License          Apache-2.0
PyPI             https://pypi.python.org/pypi/ecs_pattern/
Dependencies     dataclasses before 3.7, typing before 3.5
===============  ==========================================

.. contents::

Введение
========================================================================================================================
| ECS - Entity-Component-System - это архитектурный шаблон, созданный для разработки игр.

Он отлично подходит для описания динамического виртуального мира.

Основные принципы ECS:

* Композиция важнее наследования (Composition over inheritance)
* Данные отделены от логики (Data Oriented Design)

| *Component* - Свойство с данными объекта
| *Entity* - Контейнер для свойств
| *System* - Логика обработки данных
| *EntityManager* - База данных сущностей
| *SystemManager* - Контейнер для систем

Установка
========================================================================================================================
::

    $ pip install ecs-pattern

Руководство
========================================================================================================================

.. code-block:: python

    from ecs_pattern import component, entity, EntityManager, System, SystemManager

* Опишите компоненты - component
* Опишите сущности на основе компонентов - entity
* Распределите ответственность обработки сущностей по системам  - System
* Храните сущности в менеджере сущностей - EntityManager
* Управляйте системами менеджером систем - SystemManager

Component
------------------------------------------------------------------------------------------------------------------------
    | Свойство с данными объекта. Содержат только данные, без логики.

    | Компонент используется как миксин в сущностях.

    | Используйте декоратор ecs_pattern.component для создания компонентов.

    | Технически это python dataclass.

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
    | Контейнер для свойств. Состоит только из компонентов.

    | Запрещено добавлять атрибуты к сущности динамически.

    | Используйте декоратор ecs_pattern.entity для создания сущностей.

    | Технически это python dataclass со slots=True.

    .. code-block:: python

        @entity
        class Player(ComPosition, ComPerson):
            pass

        @entity
        class Ball(ComPosition):
            pass

System
------------------------------------------------------------------------------------------------------------------------
    | Логика обработки сущностей.

    | Не содержит данных о сущностях и компонентах.

    | Используйте абстрактный класс ecs_pattern.System для создания конкретных систем:

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
    | База данных сущностей.

    | Единая точка доступа ко всем сущностям.

    | Используйте класс ecs_pattern.EntityManager для создания менеджера сущностей.

    | Временная сложность get_by_class и get_with_component - как у словаря

    | *entities.add* - Добавить сущности.

    | *entities.delete* - Удалить сущности.

    | *entities.delete_buffer_add* - Сохранить сущности в буфер удаления, чтобы удалить позже.

    | *entities.delete_buffer_purge* - Удалить все сущности в буфере удаления и очистить буффер.

    | *entities.init* - Дать менеджеру знать о сущностях. При доступе к неизвестным объектам бросается KeyError.

    | *entities.get_by_class* - Получить все сущности указанных классов. Учитывает порядок сущностей.

    | *entities.get_with_component* - Получить все сущности с указанными компонентами.

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
    | Контейнер для систем.

    | Работает с системами в заданном порядке.

    | Используйте класс ecs_pattern.SystemManager для управления системами.

    | *system_manager.start_systems* - Инициализировать системы. Вызовите один раз перед главным циклом обновления систем.

    | *system_manager.update_systems* - Обновить состояние систем. Вызывайте в главном цикле.

    | *system_manager.stop_systems* - Завершить работу систем. Вызовите один раз после завершения главного цикла.

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

Примеры
========================================================================================================================
* `Игра Pong: pygame + ecs_pattern <https://github.com/ikvk/ecs_pattern/tree/master/examples/pong>`_.

Преимущества
========================================================================================================================
* Слабая связность кода - легко рефакторить и расширять кодовую базу
* Модульность и тестируемость логики - легко тестировать и переиспользовать код в других проектах
* Следование принципам шаблона мешает писать плохой код
* Легко соблюдать логику Single Responsibility
* Легко комбинировать свойства сущностей
* Легко анализировать производительность
* Легко распараллеливать обработку
* Легко работать с чистыми данными

Сложности
========================================================================================================================
Чтобы научиться правильно готовить ECS, может потребоваться много практики:

* Данные доступны откуда угодно - сложно искать ошибки
* Системы работают в строго друг за другом
* Рекурсивная логика не поддерживается напрямую

Ошибки новичка
========================================================================================================================
* Наследование компонентов, сущностей, систем
* Игнорирование принципов ECS, например хранение данных в системе
* Возведение ECS в абсолют, ООП никто не отменяет
* Адаптация существующего кода проекта под ECS "как есть"
* Использование рекурсивной или реактивной логики в системах
* Использование EntityManager.delete в циклах get_by_class, get_with_component

Хорошие практики
========================================================================================================================
* Используйте компоненты "одиночки (Singleton)" с данными и флагами
* Минимизируйте места изменения компонента
* Не создавайте методы в компонентах и сущностях
* Используйте пакеты для разделения сцен

Пример дерева проекта:
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

Релизы
========================================================================================================================

История важных изменений: `release_notes.rst <https://github.com/ikvk/ecs_pattern/blob/master/_docs/release_notes.rst>`_

Помощь проекту
========================================================================================================================
* Нашли ошибку или есть предложение -  issue / merge request 🎯
* Нечем помочь этому проекту - помогите другому открытому проекту, который используете ✋
* Некуда деть деньги - потратьте на семью, друзей, близких или окружающих вас людей 💰
* Поставьте проекту ⭐
