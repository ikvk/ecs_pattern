"""
ECS - Entity Component system
"""

from typing import Iterable, Iterator, Any
from dataclasses import dataclass
from functools import partial
from collections import deque

# all component classes must be decorated with this function
component = dataclass

# all entity classes must be decorated with this function
entity = partial(dataclass, slots=True)


class EntityManager:
    """Entity manager"""

    def __init__(self):
        self._entity_map = {}  # Person: [ent1, ent2]
        self._entity_components_map = {}  # Person: (MoveCom, DamageCom, NameCom)
        self._set_cache_map = {}  # (MoveCom, DamageCom, NameCom): {MoveCom, DamageCom, NameCom}
        self._delete_entity_buffer = deque()  # deque([Person1, Person2])

    def add(self, *entity_value_list: Any):
        """Add entities to world"""
        for entity_value in entity_value_list:
            assert getattr(entity_value, '__dict__', None) in (None, {}), 'Data class with inefficient memory usage'
            entity_value_class = entity_value.__class__
            self._entity_map.setdefault(entity_value_class, []).append(entity_value)
            if entity_value_class not in self._entity_components_map:
                self._entity_components_map[entity_value_class] = tuple(sorted(
                    (i for i in entity_value_class.__mro__ if i is not object),
                    key=lambda x: x.__class__.__name__
                ))

    def delete(self, *entity_value_list: Any):
        """Delete entities from world"""
        for entity_value in entity_value_list:
            self._entity_map[entity_value.__class__].remove(entity_value)

    def delete_buffer_add(self, *entity_value_list: Any):
        """Save entities into delete buffer for delete them from world later"""
        for entity_value in entity_value_list:
            self._delete_entity_buffer.append(entity_value)

    def delete_buffer_purge(self):
        """Delete all entities from delete buffer"""
        for delete_entity in self._delete_entity_buffer:
            self.delete(delete_entity)
        self._delete_entity_buffer.clear()

    def init(self, *entity_list: Any):
        """
        Let entity manager to "know" about entities before work
        If manager do not know about entity, it will raise KeyError on access to it.
        event: SomeEvent = next(self.entities.get_by_class(SomeEvent), None)
        """
        for ent in entity_list:
            self.add(ent)
            self.delete(ent)

    def get_by_class(self, *entity_class_val_list: type) -> Iterator[Any]:
        """
        Get all entities by specified entity class in specified order
        raise KeyError for uninitialized (never added) entities
        """
        for entity_class_val in entity_class_val_list:
            yield from self._entity_map[entity_class_val]

    def get_with_component(self, *component_class_val_list: type) -> Iterator[Any]:
        """
        Get all entities that contains all specified component classes
        Sometimes it will be useful to warm up the cache
        raise KeyError for uninitialized (never added) entities
        """
        for entity_class, entity_component_list in self._entity_components_map.items():
            entity_component_set = \
                self._set_cache_map.setdefault(entity_component_list, set(entity_component_list))
            component_class_val_set = \
                self._set_cache_map.setdefault(component_class_val_list, set(component_class_val_list))
            if component_class_val_set.issubset(entity_component_set):
                yield from self._entity_map[entity_class]


class System:
    """
    Abstract base class for system
    All systems must be derived from this class
    System should have data for work: implement __init__ method
    """

    def start(self):
        """
        Preparing system to work before starting SystemManager.systems_update loop
        Runs by SystemManager.start_systems
        """

    def update(self):
        """
        Run main system logic
        Runs by SystemManager.update_systems
        """

    def stop(self):
        """
        Clean system resources after stop update loop
        Runs by SystemManager.stop_systems
        """


class SystemManager:
    """System manager"""

    def __init__(self, system_list: Iterable[System]):
        """
        system_list: Ordered sequence with systems
        """
        self._system_list = tuple(system_list)
        self._system_with_start_list = tuple(i for i in self._system_list if hasattr(i, 'start'))
        self._system_with_update_list = tuple(i for i in self._system_list if hasattr(i, 'update'))
        self._system_with_stop_list = tuple(i for i in self._system_list if hasattr(i, 'stop'))

    def start_systems(self):
        """Start all systems"""
        for system in self._system_with_start_list:
            system.start()

    def update_systems(self):
        """Update all systems"""
        for system in self._system_with_update_list:
            system.update()

    def stop_systems(self):
        """Stop all systems"""
        for system in self._system_with_stop_list:
            system.stop()
