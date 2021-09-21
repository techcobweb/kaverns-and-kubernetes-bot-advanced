import unittest
import roguebot
from roguebot.navigation.point import *
from roguebot.state.dungeon_map import *
from roguebot.state.entity import Entities, Entity
from assertpy import assert_that
from roguebot.state.item import Item


class TestEntities(unittest.TestCase):
    def get_simple_entity_list(self):
        return [
            {'char': '@', 'foreground': 'yellow', 'background': 'black',
             'alive': True, 'walkable': True,
             'pos': {'x': 31, 'y': 16, 'z': 0},
             'name': 'mc', 'details': 'a brawny warrior',
             'edible': False,
             'wieldable': False, 'wearable': False,
             'id': 'aaa', 'role': 'warrior',
             'type': 'player', 'level': 0,
             'speed': 1000, 'maxHitPoints': 10,
             'hp': 10,
             'hunger': 0,
             'sight': 10, 'currentArmour': None, 'currentWeapon': None,
             'ac': 10, 'inventory': [],
             'corpse': {'char': '%', 'foreground': 'red', 'background': 'black',
                        'alive': False, 'walkable': True}, 'pos': {'x': 0, 'y': 0, 'z': 0},
             'rules': {}, 'damage': 1, 'hitBonus': 1, 'base_ac': 10,
             'entrance': {'x': 31, 'y': 16, 'z': 0}
             },
            {'char': 'O', 'foreground': 'yellow', 'background': 'black',
             'alive': True, 'walkable': True,
             'pos': {'x': 1, 'y': 2, 'z': 3},
             'name': 'george', 'details': 'a brawny warrior', 'edible': False,
             'wieldable': False,
             'wearable': False,
             'id': 'bbb', 'role': 'warrior',
             'level': 0, 'speed': 1000, 'maxHitPoints': 10, 'hp': 10,
             'hunger': 0
             }
        ]

    def test_can_delete_null_entity_does_nothing(self):
        entities = Entities.from_wire_format(self.get_simple_entity_list())
        entities.delete(None)

    def test_can_add_null_entity_does_nothing(self):
        entities = Entities.from_wire_format(self.get_simple_entity_list())
        entities.add(None)

    def test_can_update_null_entity_does_nothing(self):
        entities = Entities.from_wire_format(self.get_simple_entity_list())
        entities.update(None)

    def test_can_get_entity_by_id(self):
        entities = Entities.from_wire_format(self.get_simple_entity_list())
        entity_got = entities.get_by_id('aaa')
        self.assertEqual('mc', entity_got.name)

    def test_can_get_all_entity(self):
        entities = Entities.from_wire_format(self.get_simple_entity_list())
        entities_got = entities.get_all()
        assert_that(entities_got).is_length(2)

    def test_can_update_entity_position(self):
        entities = Entities.from_wire_format(self.get_simple_entity_list())
        id = 'aaa'
        new_position = Point(1, 2, 3)
        entity_got = entities.get_by_id(id)
        self.assertNotEqual(new_position, entity_got.position)

        entities.update_position(id, new_position)
        entity_got = entities.get_by_id(id)
        self.assertEqual(new_position, entity_got.position)

    def test_can_render_entity_list_as_string(self):
        entities = Entities.from_wire_format(self.get_simple_entity_list())
        s = str(entities)
        assert_that(s).contains('aaa')

    def test_can_get_entity_by_position(self):
        entities = Entities.from_wire_format(self.get_simple_entity_list())
        id = 'aaa'
        start_entity = entities.get_by_id(id)
        entities.update_position(id, Point(1, 2, 3))
        entities_at_point = entities.get_by_position(Point(1, 2, 3))
        assert_that(entities_at_point).contains(start_entity)

    def test_entity_can_be_updated(self):
        entity_list_data = self.get_simple_entity_list()
        entities = Entities.from_wire_format(entity_list_data)
        old_entity = entities.get_by_id("aaa")
        identifier = old_entity.entity_id

        new_entity = Entity(char="P", name="pilgrim", position=Point(
            1, 2, 0), identifier=identifier)
        entities.update(new_entity)

        got_back = entities.get_by_id(identifier)
        assert_that(got_back.char).is_equal_to("P")


class TestEntity(unittest.TestCase):

    def get_simple_entity_list(self):
        return [
            {'char': '@', 'foreground': 'yellow', 'background': 'black',
             'alive': True, 'walkable': True, 'pos': {'x': 31, 'y': 16, 'z': 0},
             'name': 'mc', 'details': 'a brawny warrior', 'edible': False,
             'wieldable': False, 'wearable': False, 'id': 'aaa', 'role': 'warrior',
             'type': 'player', 'level': 0, 'speed': 1000, 'maxHitPoints': 10,
             'hitPoints': 10, 'hunger': 0,
             'sight': 10, 'currentArmour': None, 'currentWeapon': None, 'ac': 10,
             'inventory': [], 'corpse': {'char': '%', 'foreground': 'red',
                                         'background': 'black', 'alive': False, 'walkable': True,
                                         'pos': {'x': 0, 'y': 0, 'z': 0},
                                         'name': 'warrior corpse', 'details': 'none', 'edible': False,
                                         'wieldable': False, 'wearable': False}
             },
            {'char': 'O', 'foreground': 'yellow', 'background': 'black',
             'alive': False, 'walkable': True, 'pos': {'x': 1, 'y': 2, 'z': 3},
             'name': 'george', 'details': 'a brawny warrior', 'edible': False,
             'wieldable': False, 'wearable': False, 'id': 'bbb', 'role': 'warrior',
             'level': 0, 'speed': 1000, 'maxHitPoints': 10, 'hitPoints': 10,
             'hunger': 0
             }
        ]

    def test_recognises_chars(self):
        entity_list_data = self.get_simple_entity_list()
        entities = Entities.from_wire_format(entity_list_data)
        self.assertEqual(2, len(entities))
        self.assertEqual('@', entities.get_by_id('aaa').char)
        self.assertEqual('O', entities.get_by_id('bbb').char)

    def test_recognises_name(self):
        entity_list_data = self.get_simple_entity_list()
        entities = Entities.from_wire_format(entity_list_data)
        self.assertEqual(2, len(entities))
        self.assertEqual('mc', entities.get_by_id('aaa').name)
        self.assertEqual('george', entities.get_by_id('bbb').name)

    def test_recognises_position(self):
        entity_list_data = self.get_simple_entity_list()
        entities = Entities.from_wire_format(entity_list_data)
        self.assertEqual(2, len(entities))
        self.assertEqual(Point(31, 16, 0), entities.get_by_id('aaa').position)
        self.assertEqual(Point(1, 2, 3), entities.get_by_id('bbb').position)

    def test_recognises_is_alive_true(self):
        entity_list_data = self.get_simple_entity_list()

        entities = Entities.from_wire_format(entity_list_data)

        assert_that(entities.get_by_id('aaa').alive).is_true()

    def test_recognises_is_alive_false(self):
        entity_list_data = self.get_simple_entity_list()

        entities = Entities.from_wire_format(entity_list_data)

        assert_that(entities.get_by_id('bbb').alive).is_false()

    def test_renders_to_string(self):
        entity_list_data = self.get_simple_entity_list()
        entities = Entities.from_wire_format(entity_list_data)
        entity_under_test = entities.get_by_id('aaa')
        result = str(entity_under_test)
        assert_that(result).contains("Entity(").contains(
            "id").contains(" char").contains(" position").contains(" weapon").contains(" armour")

    def test_repr_renders_ok(self):
        entity = Entity(char="A", name="harry",
                        position=Point(1, 1, 0), identifier="myId")
        assert_that(str([entity])).contains("Entity(").contains(
            "id").contains(" char").contains(" position").contains(" weapon").contains(" armour")

    def test_can_get_identifier(self):
        entity = Entity(char="A", name="harry",
                        position=Point(1, 1, 0), identifier="myId")
        assert_that(entity.identifier).is_equal_to("myId")

    def test_can_set_and_get_position(self):
        entity_list_data = self.get_simple_entity_list()
        entities = Entities.from_wire_format(entity_list_data)
        entity_under_test = entities.get_by_id('aaa')
        expected = Point(12, 13, 14)
        entity_under_test.position = expected
        got_back = entity_under_test.position
        assert_that(got_back).is_equal_to(expected)

    def test_deleting_entity_removes_it_from_all_indexes(self):
        entity_list_data = self.get_simple_entity_list()
        entities = Entities.from_wire_format(entity_list_data)
        entity_under_test = entities.get_by_id('aaa')
        point = entity_under_test.position

        entities.delete_at_position(point)

        assert_that(entities.get_by_id(entity_under_test.entity_id)).is_none()
        assert_that(entities.get_by_position(point)).is_empty()

    def test_deleting_entity_not_(self):
        entity_list_data = self.get_simple_entity_list()
        entities = Entities.from_wire_format(entity_list_data)
        entity_under_test = entities.get_by_id('aaa')
        point = entity_under_test.position

        entities.delete_at_position(point)

        assert_that(entities.get_by_id(entity_under_test.entity_id)).is_none()
        assert_that(entities.get_by_position(point)).is_empty()

    def test_deleting_entity_when_there_are_two_in_one_place_picks_one_using_id(self):
        entities = Entities()
        fred = Entity(char="A", name="fred",
                      position=Point(1, 1, 1), identifier="fredID")
        joe = Entity(char="A", name="joe", position=Point(
            1, 1, 1), identifier="joeID")
        entities.add(fred)
        entities.add(joe)

        entities.delete(joe)

        assert_that(entities.get_all()).contains(fred).does_not_contain(joe)

    def test_deleting_entity_when_there_are_two_in_one_place_picks_one_using_id2(self):
        entities = Entities()
        fred = Entity(char="A", name="fred",
                      position=Point(1, 1, 1), identifier="fredID")
        joe = Entity(char="A", name="joe", position=Point(
            1, 1, 1), identifier="joeID")
        entities.add(fred)
        entities.add(joe)

        entities.delete(fred)

        assert_that(entities.get_all()).contains(joe).does_not_contain(fred)

    def test_entity_can_have_empty_inventory_from_wire_format(self):
        entity_list_data = self.get_simple_entity_list()
        entities = Entities.from_wire_format(entity_list_data)
        mc_entity = entities.get_by_id("aaa")
        assert_that(mc_entity.inventory).is_empty()

    def test_entity_can_have_an_inventory(self):
        hat = Item(Point(1, 1, 1), name="hat", edible=False,
                   wieldable=False, wearable=True)
        entity = Entity(char="@", name="fred", position=Point(1,
                        1, 1), identifier="myId", alive=True, inventory=[hat])
        assert_that(entity.inventory).contains(hat)

    def load_complex_entity_from_wire_format(self) -> Entity:
        entity_wire_format = {
            'char': '@', 'foreground': 'yellow', 'background': 'black',
            'alive': True, 'walkable': True, 'pos': {'x': 31, 'y': 16, 'z': 0},
            'name': 'mc', 'details': 'a brawny warrior', 'edible': False,
            'wieldable': False, 'wearable': False, 'id': 'aaa', 'role': 'warrior',
            'type': 'player', 'level': 0, 'speed': 1000, 'maxHitPoints': 10,
            'hitPoints': 10, 'hunger': 5,
            'sight': 10,
            'currentArmour': {'char': 'L', 'foreground': 'grey',
                              'background': 'black', 'alive': False,
                              'walkable': True, 'pos': {'x': 28, 'y': 6, 'z': 0},
                              'name': 'chainmail', 'details': 'chain links',
                              'edible': False, 'wieldable': False,
                              'wearable': True, 'ac': 5
                              },
            'currentWeapon': {'char': '*', 'foreground': 'grey',
                              'background': 'black', 'alive': False,
                              'walkable': True, 'pos': {'x': 28, 'y': 6, 'z': 0},
                              'name': 'rock', 'details': 'igneous',
                              'edible': False, 'wieldable': True,
                              'wearable': False, 'damage': 2
                              },
            'ac': 10,
            'inventory': [
                {'char': '*', 'foreground': 'grey',
                 'background': 'black', 'alive': False,
                 'walkable': True, 'pos': {'x': 28, 'y': 6, 'z': 0},
                 'name': 'rock', 'details': 'igneous',
                 'edible': False, 'wieldable': True,
                 'wearable': False, 'damage': 2
                 },
                {'char': 'L', 'foreground': 'grey',
                 'background': 'black', 'alive': False,
                 'walkable': True, 'pos': {'x': 28, 'y': 6, 'z': 0},
                 'name': 'chainmail', 'details': 'chain links',
                 'edible': False, 'wieldable': False,
                 'wearable': True, 'ac': 5
                 }
            ], 'corpse': {'char': '%', 'foreground': 'red',
                          'background': 'black', 'alive': False, 'walkable': True,
                          'pos': {'x': 0, 'y': 0, 'z': 0},
                          'name': 'warrior corpse', 'details': 'none', 'edible': False,
                          'wieldable': False, 'wearable': False}
        }

        entity = Entity.from_wire_format(entity_wire_format)
        return entity

    def test_entity_can_have_a_non_empty_inventory_from_wire_format(self):
        entity = self.load_complex_entity_from_wire_format()
        assert_that(entity.inventory).is_not_empty()
        assert_that(entity.inventory[0].name).is_equal_to("rock")

    def test_entity_can_have_a_non_empty_current_weapon_from_wire_format(self):
        entity = self.load_complex_entity_from_wire_format()
        assert_that(entity.current_weapon).is_not_none()
        assert_that(entity.current_weapon.name).is_equal_to("rock")

    def test_entity_can_have_an_armor_class(self):
        entity = self.load_complex_entity_from_wire_format()
        assert_that(entity.armour_class).is_not_none().is_equal_to(10)

    def test_entity_can_have_an_hit_points(self):
        entity = self.load_complex_entity_from_wire_format()
        assert_that(entity.hit_points).is_not_none().is_equal_to(10)

    def test_can_see_current_armour(self):
        entity = self.load_complex_entity_from_wire_format()
        assert_that(entity.current_armour.name).is_not_none(
        ).is_equal_to("chainmail")

    def test_entity_has_hunger(self):
        entity = self.load_complex_entity_from_wire_format()
        assert_that(entity.hunger).is_not_none().is_equal_to(5)

    def test_entity_has_settable_hunger(self):
        entity = self.load_complex_entity_from_wire_format()
        assert_that(entity.hunger).is_not_none().is_equal_to(5)
        entity.hunger = 10
        assert_that(entity.hunger).is_not_none().is_equal_to(10)

    def test_can_set_current_armour(self):
        entity = Entity(char="A",
                        name="freda",
                        position=Point(1, 1, 0),
                        identifier="aaa",
                        current_weapon=None,
                        armour_class=10,
                        hit_points=10,
                        current_armour=None,

                        hunger=0
                        )
        dress = Item(position=Point(1, 1, 0), name="dress")
        entity.inventory.append(dress)

        entity.current_armour = dress

        assert_that(entity.current_armour.name).is_equal_to(dress.name)

    def test_can_set_current_weapon(self):
        entity = Entity(char="A",
                        name="freda",
                        position=Point(1, 1, 0),
                        identifier="aaa",
                        current_weapon=None,
                        armour_class=10,
                        hit_points=10,
                        current_armour=None,

                        hunger=0
                        )
        katana = Item(position=Point(1, 1, 0), name="katana")
        entity.inventory.append(katana)

        entity.current_weapon = katana

        assert_that(entity.current_weapon.name).is_equal_to(katana.name)
