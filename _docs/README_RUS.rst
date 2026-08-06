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

🧭 Введение
========================================================================================================================
| ECS - Entity-Component-System - это архитектурный шаблон, созданный для разработки игр.

Он отлично подходит для описания динамического виртуального мира.

Основные принципы ECS:

* Композиция важнее наследования (Composition over inheritance)
* Данные отделены от логики (Data Oriented Design)

| ``Component`` - Свойство с данными объекта
| ``Entity`` - Контейнер для свойств
| ``System`` - Логика обработки данных
| ``EntityManager`` - База данных сущностей
| ``SystemManager`` - Контейнер для систем

⚙️ Установка
========================================================================================================================
::

    $ pip install ecs-pattern

📘 Руководство
========================================================================================================================

Библиотека предоставляет вам 5 инструментов:

.. code-block:: python

    from ecs_pattern import component, entity, EntityManager, System, SystemManager

* Опишите компоненты - ``component``
* Опишите сущности на основе компонентов - ``entity``
* Распределите ответственность обработки сущностей по системам  - ``System``
* Храните сущности в менеджере сущностей - ``EntityManager``
* Управляйте системами менеджером систем - ``SystemManager``

🧩 Component
------------------------------------------------------------------------------------------------------------------------
    | Свойство с данными объекта. Содержат только данные, без логики.

    | Используйте декоратор ecs_pattern.component для создания компонентов.

    | Технически это python dataclass.

    | Используйте компоненты как миксины для сущностей.

    .. code-block:: python

        @component
        class ComPosition:
            x: int = 0
            y: int = 0

        @component
        class ComPerson:
            name: str
            health: int

🧱 Entity
------------------------------------------------------------------------------------------------------------------------
    | Контейнер для свойств. Состоит только из компонентов.

    | Запрещено добавлять атрибуты к сущности динамически.

    | Используйте декоратор ecs_pattern.entity для создания сущностей.

    | Технически это python dataclass со slots=True.

    | Используйте EntityManager для хранения сущностей.

    .. code-block:: python

        @entity
        class Player(ComPosition, ComPerson):
            pass

        @entity
        class Ball(ComPosition):
            pass

🔄 System
------------------------------------------------------------------------------------------------------------------------
    | Логика обработки сущностей.

    | Не содержит данных о сущностях и компонентах.

    | Используйте абстрактный класс ecs_pattern.System для создания конкретных систем:

    | *system.start* - Инициализировать систему. Вызывается один раз перед основным циклом обновления системы.

    | *system.update* - Обновить состояние системы. Вызывается в основном цикле.

    | *system.stop* - Остановка системы. Вызывается один раз после завершения основного цикла.

    | Используйте SystemManager для управления системами.

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

🗂️ EntityManager
------------------------------------------------------------------------------------------------------------------------
    | Контейнер для сущностей.

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

🗃️ SystemManager
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

💡 Примеры
========================================================================================================================
* `Pong <https://github.com/ikvk/ecs_pattern/tree/master/examples/pong#pong---classic-game>`_: игра - pygame + ecs_pattern
* `Snow day <https://github.com/ikvk/ecs_pattern/tree/master/examples/snow_day#snow-day---scene>`_: сцена - pygame + ecs_pattern
* `Trig fall <https://github.com/ikvk/ecs_pattern/tree/master/examples/trig#trig-fall---game>`_: коммерческая игра - pygame + ecs_pattern + numpy
* `Advanced GUI <https://github.com/ikvk/ecs_pattern/tree/master/examples/gui>`_: Продвинутый графический интерфейс из реального проекта
* `Compare with esper <https://github.com/ikvk/ecs_pattern/tree/master/examples/compare_with_esper>`_: другая библиотека ECS для python.
* `entity_strict.py <https://github.com/ikvk/ecs_pattern/tree/master/examples/entity_strict.py>`_: entity ``для отладки``, который запрещает создание новых атрибутов.

🌟 Преимущества
========================================================================================================================
* Эффективное использования памяти - Component и Entity используют dataclass
* Удобный поиск объектов - по классу сущности и по компонентам сущности
* Гибкость - слабая связность в коде позволяет быстро расширять проект
* Модульность - код легко тестировать, анализировать производительность, переиспользовать
* Контроль за выполнением - системы работают строго друг за другом
* Следование принципам шаблона помогает писать качественный код
* Удобно распараллеливать обработку
* Компактная реализация

⚠️ Сложности
========================================================================================================================
* Чтобы научиться правильно готовить ECS, может потребоваться много практики
* Данные доступны откуда угодно - сложно искать ошибки

❌ Ошибки новичка
========================================================================================================================
* Наследование компонентов, сущностей, систем
* Игнорирование принципов ECS, например хранение данных в системе
* Возведение ECS в абсолют, ООП никто не отменяет
* Адаптация существующего кода проекта под ECS "как есть"
* Использование рекурсивной или реактивной логики в системах
* Использование EntityManager.delete в циклах get_by_class, get_with_component
* Динамическое добавление атрибутов в сущность

✅ Хорошие практики
========================================================================================================================
* Используйте компоненты "одиночки (Singleton)" с данными и флагами, например для событий
* Минимизируйте места изменения компонента
* Не создавайте методы в компонентах и сущностях
* Делите проект на сцены, сценой можно считать цикл для SystemManager с его EntityManager
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

🛠️ Суть реализации
========================================================================================================================

В классической реализации ECS - каждый компонент хранится в отдельной коллекции.
В python невозможно разместить объекты в непрерывной памяти,
поэтому оптимизация доступа процессора к памяти в python не реализуема.

Библиотека ecs_pattern делает упор на простоту и удобство работы с объектами в коде.

Если вам оказалось недостаточно скорости доступа к объектам (например миллион объектов),
то меняйте язык на более быстрый - без вариантов.

📜 Релизы
========================================================================================================================

История важных изменений: `release_notes.rst <https://github.com/ikvk/ecs_pattern/blob/master/_docs/release_notes.rst>`_

🤝 Помощь проекту
========================================================================================================================
* Нашли ошибку или есть предложение -  issue / merge request 🎯
* Нечем помочь этому проекту - помогите другому открытому проекту, который используете ✋
* Некуда деть деньги - потратьте на семью, друзей, близких или окружающих вас людей 💰
* Поставьте проекту ⭐
