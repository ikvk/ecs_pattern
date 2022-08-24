import unittest

from pyecs.ecs import component, entity, EntityManager, System, SystemManager


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
        for com_with_pos in self.entities.get_with_component(ComPosition):
            com_with_pos: ComPosition
            if com_with_pos.y > 0:
                com_with_pos.y -= 1

    def stop(self):
        self._gravitation_enabled = False


class SysPersonHealthRegeneration(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self._regeneration_enabled = False

    def start(self):
        self._regeneration_enabled = True

    def update(self):
        if not self._regeneration_enabled:
            return
        for com_with_health in self.entities.get_with_component(ComPerson):
            com_with_health: ComPerson
            if com_with_health.health < 100:
                com_with_health.health += 1

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

        entities.add(player1, player2, ball)
        self.assertEqual(len(list(entities.get_by_class(Player))), 2)
        self.assertEqual(len(list(entities.get_by_class(Ball))), 1)
        self.assertEqual(len(list(entities.get_by_class(Ball, Player))), 3)
        self.assertEqual(list(entities.get_by_class(Ball, Player)), [ball, player1, player2])
        self.assertEqual(len(list(entities.get_with_component(ComPosition))), 3)
        self.assertEqual(len(list(entities.get_with_component(ComPerson))), 2)
        self.assertEqual(len(list(entities.get_with_component(ComPerson, ComPosition))), 2)  # *and

        entities.delete(player1, player2)
        self.assertEqual(len(list(entities.get_by_class(Player))), 0)
        self.assertEqual(len(list(entities.get_by_class(Ball))), 1)
        self.assertEqual(len(list(entities.get_with_component(ComPosition))), 1)
        self.assertEqual(len(list(entities.get_with_component(ComPerson))), 0)

        entities.delete(ball)
        self.assertEqual(len(list(entities.get_by_class(Player))), 0)
        self.assertEqual(len(list(entities.get_by_class(Ball))), 0)
        self.assertEqual(len(list(entities.get_with_component(ComPosition))), 0)
        self.assertEqual(len(list(entities.get_with_component(ComPerson))), 0)

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
        system_manager = SystemManager([sys_regen, sys_grav])
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


if __name__ == "__main__":
    unittest.main()
