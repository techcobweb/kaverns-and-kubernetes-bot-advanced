import pytest
import types
import unittest
import roguebot

from assertpy import assert_that
from roguebot.state.item import Items, Item
from roguebot.navigation.point import Point


class TestItem(unittest.TestCase):
    def get_item_raw_dataA(self) -> dict:
        return {'char': 'o', 'foreground': 'green',
                'background': 'black', 'alive': False, 'walkable': True,
                'pos': {'x': 22, 'y': 16, 'z': 0}, 'name': 'apple',
                'details': 'it looks edible',
                'edible': True, 'wieldable': True, 'wearable': True,
                'damage': 2, 'ac': 5
                }

    def get_item_raw_dataB(self) -> dict:
        return {'char': 'o', 'foreground': 'green',
                'background': 'black', 'alive': False, 'walkable': False,
                'pos': {'x': 22, 'y': 16, 'z': 0}, 'name': 'apple',
                'details': 'it looks edible',
                'edible': False, 'wieldable': False, 'wearable': False
                }

    def test_item_renders_to_string(self):
        data = self.get_item_raw_dataA()
        item = Item.from_wire_format(data)
        assert_that(str(item)) \
            .contains("Item") \
            .contains("Point") \
            .contains("edible") \
            .contains("wearable")

    def test_item_repr_renders_to_string(self):
        data = self.get_item_raw_dataA()
        item = Item.from_wire_format(data)
        assert_that(str([item])) \
            .contains("Item") \
            .contains("Point") \
            .contains("edible") \
            .contains("wearable")

    def test_parses_edible_true(self):
        data = self.get_item_raw_dataA()
        item = Item.from_wire_format(data)
        assert_that(item.edible).is_equal_to(True)

    def test_parses_edible_false(self):
        data = self.get_item_raw_dataB()
        item = Item.from_wire_format(data)
        assert_that(item.edible).is_equal_to(False)

    def test_parses_wieldable_true(self):
        data = self.get_item_raw_dataA()
        item = Item.from_wire_format(data)
        assert_that(item.wieldable).is_equal_to(True)

    def test_parses_wieldable_false(self):
        data = self.get_item_raw_dataB()
        item = Item.from_wire_format(data)
        assert_that(item.wieldable).is_equal_to(False)

    def test_parses_wearable_true(self):
        data = self.get_item_raw_dataA()
        item = Item.from_wire_format(data)
        assert_that(item.wearable).is_equal_to(True)

    def test_parses_wearable_false(self):
        data = self.get_item_raw_dataB()
        item = Item.from_wire_format(data)
        assert_that(item.wearable).is_equal_to(False)

    def test_parses_name(self):
        data = self.get_item_raw_dataA()
        item = Item.from_wire_format(data)
        assert_that(item.name).is_equal_to("apple")

    def test_parses_damage(self):
        data = self.get_item_raw_dataA()
        item = Item.from_wire_format(data)
        assert_that(item.damage).is_not_none().is_equal_to(2)

    def test_parses_no_damage(self):
        data = self.get_item_raw_dataB()
        item = Item.from_wire_format(data)
        assert_that(item.damage).is_not_none().is_equal_to(0)

    def test_can_get_and_set_initial_position(self):
        item = Item(name='mango', position=Point(1, 1, 0))
        assert_that(item.position).is_equal_to(Point(1, 1, 0))

    def test_can_get_and_set_position_after_construction(self):
        item = Item(name='mango', position=Point(1, 1, 0))

        item.position = Point(2, 2, 0)

        assert_that(item.position).is_equal_to(Point(2, 2, 0))

    def test_parses_armour_class(self):
        data = self.get_item_raw_dataA()
        item = Item.from_wire_format(data)
        assert_that(item.armour_class).is_not_none().is_equal_to(5)

    def test_parses_no_armour_class(self):
        data = self.get_item_raw_dataB()
        item = Item.from_wire_format(data)
        assert_that(item.armour_class).is_not_none().is_equal_to(10)
