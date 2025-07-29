import unittest
from time import monotonic

from ecs_pattern import component, entity, EntityManager, System, SystemManager


@component
class ComPosition:
    x: int = 0
    y: int = 0


@component
class ComPerson:
    name: str
    health: int


@entity
class Player(ComPosition, ComPerson):
    pass


@entity
class Ball(ComPosition):
    pass


class SysGravitation(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self._gravitation_enabled = False

    def start(self):
        self._gravitation_enabled = True

    def update(self):
        if not self._gravitation_enabled:
            return
        for entity_with_pos in self.entities.get_with_component(ComPosition):
            if entity_with_pos.y > 0:
                entity_with_pos.y -= 1

    def stop(self):
        self._gravitation_enabled = False


class SysInit(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.some_init_data = None

    def start(self):
        self.some_init_data = 123

    def stop(self):
        self.some_init_data = None


class SysLive(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.live_data = None

    def update(self):
        self.live_data = monotonic() % 2


class SysPersonHealthRegeneration(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self._regeneration_enabled = False

    def start(self):
        self._regeneration_enabled = True

    def update(self):
        if not self._regeneration_enabled:
            return
        for entity_with_health in self.entities.get_with_component(ComPerson):
            entity_with_health: ComPerson
            if entity_with_health.health < 100:
                entity_with_health.health += 1

    def stop(self):
        self._regeneration_enabled = False


class EcsTest(unittest.TestCase):
    def test_component(self):
        position = ComPosition(1, 2)
        self.assertEqual((position.x, position.y), (1, 2))
        person = ComPerson('Ivan', 100)
        self.assertEqual(person.name, 'Ivan')
        self.assertEqual(person.health, 100)
        with self.assertRaises(TypeError):
            ComPerson()

    def test_entity(self):
        player = Player('Vladimir', 33, 3, 4)
        self.assertEqual((player.name, player.health, player.x, player.y), ('Vladimir', 33, 3, 4))
        ball = Ball(13, 14)
        self.assertEqual((ball.x, ball.y), (13, 14))
        with self.assertRaises(TypeError):
            Player()
        with self.assertRaises(TypeError):
            @entity
            class PlayerWrongOrderSuperClass(ComPerson, ComPosition):  # noqa
                pass

    def test_entitymanager(self):
        player1 = Player('Ivan', 20, 1, 2)
        player2 = Player('Vladimir', 30, 3, 4)
        ball = Ball(13, 24)
        entities = EntityManager()

        with self.assertRaises(KeyError):
            next(entities.get_by_class(Ball))
        entities.init(Ball(1, 1))
        self.assertEqual(next(entities.get_by_class(Ball), None), None)
        entities.delete(*tuple(entities.get_by_class(Ball)))  # no balls, no raise

        entities.add(player1, player2, ball)
        self.assertEqual(len(list(entities.get_by_class(Player))), 2)
        self.assertEqual(len(list(entities.get_by_class(Ball))), 1)
        self.assertEqual(len(list(entities.get_by_class(Ball, Player))), 3)
        self.assertEqual(list(entities.get_by_class(Ball, Player)), [ball, player1, player2])
        self.assertEqual(len(list(entities.get_with_component(ComPosition))), 3)
        self.assertEqual(len(list(entities.get_with_component(ComPerson))), 2)
        self.assertEqual(len(list(entities.get_with_component(ComPerson, ComPosition))), 2)  # *and
        self.assertEqual(len(list(entities.get_with_component(ComPerson, ComPerson, ComPerson))), 2)  # *not uniq coms

        entities.delete(player1, player2)
        self.assertEqual(len(list(entities.get_by_class(Player))), 0)
        self.assertEqual(len(list(entities.get_by_class(Ball))), 1)
        self.assertEqual(len(list(entities.get_with_component(ComPosition))), 1)
        self.assertEqual(len(list(entities.get_with_component(ComPerson))), 0)
        self.assertEqual(len(list(entities.get_with_component(ComPerson, ComPosition))), 0)

        entities.delete(ball)
        self.assertEqual(len(list(entities.get_by_class(Player))), 0)
        self.assertEqual(len(list(entities.get_by_class(Ball))), 0)
        self.assertEqual(len(list(entities.get_with_component(ComPosition))), 0)
        self.assertEqual(len(list(entities.get_with_component(ComPerson))), 0)

        # mark to del
        entities.add(player1, player2)
        self.assertEqual(len(list(entities.get_by_class(Player))), 2)
        entities.delete_buffer_purge()
        self.assertEqual(len(list(entities.get_by_class(Player))), 2)
        entities.delete_buffer_add(player1, player2)
        entities.delete_buffer_purge()
        self.assertEqual(len(list(entities.get_by_class(Player))), 0)

        # mark to del twice
        entities.add(player1, player2)
        self.assertEqual(len(list(entities.get_by_class(Player))), 2)
        entities.delete_buffer_purge()
        self.assertEqual(len(list(entities.get_by_class(Player))), 2)
        entities.delete_buffer_add(player1, player2)
        entities.delete_buffer_add(player1, player2)
        entities.delete_buffer_purge()
        self.assertEqual(len(list(entities.get_by_class(Player))), 0)

    def test_system(self):
        player1 = Player('Ivan', 20, 1, 2)
        player2 = Player('Vladimir', 30, 3, 4)
        ball = Ball(13, 24)
        entities = EntityManager()
        entities.add(player1, player2, ball)
        sys_regen = SysPersonHealthRegeneration(entities)
        i: ComPerson

        sys_regen.update()
        self.assertEqual(set(i.health for i in entities.get_with_component(ComPerson)), {20, 30})

        sys_regen.start()
        sys_regen.update()
        self.assertEqual(set(i.health for i in entities.get_with_component(ComPerson)), {21, 31})
        sys_regen.update()
        sys_regen.update()
        self.assertEqual(set(i.health for i in entities.get_with_component(ComPerson)), {23, 33})

        sys_regen.stop()
        sys_regen.update()
        self.assertEqual(set(i.health for i in entities.get_with_component(ComPerson)), {23, 33})

    def test_system_manager(self):
        player1 = Player('Ivan', 20, 1, 2)
        player2 = Player('Vladimir', 30, 3, 4)
        ball = Ball(0, 7)
        entities = EntityManager()
        entities.add(player1, player2, ball)
        sys_regen = SysPersonHealthRegeneration(entities)
        sys_grav = SysGravitation(entities)
        sys_init = SysInit(entities)
        sys_live = SysLive(entities)
        system_manager = SystemManager([sys_regen, sys_grav, sys_init, sys_live])
        per: ComPerson
        pos: ComPosition

        self.assertEqual(sys_regen._regeneration_enabled, False)
        self.assertEqual(sys_grav._gravitation_enabled, False)

        system_manager.start_systems()
        self.assertEqual(sys_regen._regeneration_enabled, True)
        self.assertEqual(sys_grav._gravitation_enabled, True)

        system_manager.update_systems()
        self.assertEqual(set(per.health for per in entities.get_with_component(ComPerson)), {21, 31})
        self.assertEqual(set(pos.y for pos in entities.get_with_component(ComPosition)), {1, 3, 6})
        system_manager.update_systems()
        system_manager.update_systems()
        self.assertEqual(set(per.health for per in entities.get_with_component(ComPerson)), {23, 33})
        self.assertEqual(set(pos.y for pos in entities.get_with_component(ComPosition)), {0, 1, 4})

        system_manager.stop_systems()
        self.assertEqual(sys_regen._regeneration_enabled, False)
        self.assertEqual(sys_grav._gravitation_enabled, False)
        system_manager.update_systems()
        system_manager.update_systems()
        self.assertEqual(set(per.health for per in entities.get_with_component(ComPerson)), {23, 33})
        self.assertEqual(set(pos.y for pos in entities.get_with_component(ComPosition)), {0, 1, 4})

        self.assertEqual(len(system_manager._system_with_start_list), 3)
        self.assertEqual(len(system_manager._system_with_update_list), 3)
        self.assertEqual(len(system_manager._system_with_stop_list), 3)

        self.assertEqual(
            {SysPersonHealthRegeneration, SysGravitation, SysInit},
            set(i.__class__ for i in system_manager._system_with_start_list)
        )
        self.assertEqual(
            {SysPersonHealthRegeneration, SysGravitation, SysLive},
            set(i.__class__ for i in system_manager._system_with_update_list)
        )
        self.assertEqual(
            {SysPersonHealthRegeneration, SysGravitation, SysInit},
            set(i.__class__ for i in system_manager._system_with_stop_list)
        )


if __name__ == "__main__":
    unittest.main()
