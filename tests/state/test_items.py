import pytest
import types
import unittest
import roguebot

from assertpy import assert_that
from roguebot.state.item import Items, Item
from roguebot.navigation.point import Point


@pytest.fixture
def raw_item_data() -> {str: []}:
    return {'(22,16,0)': [
        {'char': 'o', 'foreground': 'green',
            'background': 'black',
            'alive': False, 'walkable': True,
            'pos': {'x': 22, 'y': 16, 'z': 0},
            'name': 'apple',
            'details': 'it looks edible',
            'edible': True, 'wieldable': False,
            'wearable': False
         }
    ],
        '(28, 6,0)': [
        {'char': '*', 'foreground': 'grey',
            'background': 'black', 'alive': False,
            'walkable': True, 'pos': {'x': 28, 'y': 6, 'z': 0},
            'name': 'rock', 'details': 'igneous',
            'edible': False, 'wieldable': True,
            'wearable': False, 'damage': 2
         },
        {'char': '*', 'foreground': 'grey',
            'background': 'black', 'alive': False,
            'walkable': True, 'pos': {'x': 28, 'y': 6, 'z': 0},
            'name': 'rock', 'details': 'igneous',
            'edible': False, 'wieldable': True,
            'wearable': False, 'damage': 2
         }
    ]
    }


@pytest.fixture
def single_item_raw_data() -> {str: []}:
    # A single item on a different level to the other items.
    return {'(22,16,0)': [
        {'char': 'o', 'foreground': 'green',
            'background': 'black', 'alive': False,
            'walkable': True, 'pos': {'x': 22, 'y': 16, 'z': 1},
            'name': 'apple', 'details': 'it looks edible',
            'edible': True, 'wieldable': False, 'wearable': False
         }
    ]
    }


def test_parses_single_item_at_location(raw_item_data):
    items = Items()

    items.update_items(raw_item_data, Point(22, 16, 0))

    item_list = items.get_items_at_position(Point(22, 16, 0))
    assert_that(item_list).is_not_none().is_length(1)
    item = item_list.pop()
    assert_that(item.position).is_equal_to(Point(22, 16, 0))


def test_renders_ok_to_a_string(raw_item_data):
    items = Items()
    items.update_items(raw_item_data, Point(22, 16, 0))

    s = str(items)
    assert_that(s).contains("apple").contains("rock")


def test_can_get_all_items(raw_item_data):
    items = Items()
    items.update_items(raw_item_data, Point(22, 16, 0))
    assert_that(items.get_as_list()).is_length(3)


def test_can_get_length_of_items_list(raw_item_data):
    items = Items()
    items.update_items(raw_item_data, Point(22, 16, 0))
    assert_that(len(items)).is_equal_to(3)


def test_parses_two_items_at_same_location(raw_item_data):
    items = Items()
    items.update_items(raw_item_data, Point(22, 16, 0))
    item_list = items.get_items_at_position(Point(28, 6, 0))
    assert_that(item_list).is_not_none().is_length(2)
    item = item_list.pop()
    assert_that(item.position).is_equal_to(Point(28, 6, 0))


def test_can_delete_itemparses_two_items_at_same_location(raw_item_data):
    items = Items()
    items.update_items(raw_item_data, Point(22, 16, 0))
    item_list = items.get_items_at_position(Point(28, 6, 0))
    assert_that(item_list).is_not_none().is_length(2)
    item_to_delete = item_list[0]

    items.delete(item_to_delete)

    item_list = items.get_items_at_position(Point(28, 6, 0))
    assert_that(item_list).is_not_none().is_length(1)
    item = item_list.pop()
    assert_that(item.position).is_equal_to(Point(28, 6, 0))


def test_retains_items_on_other_floors_when_items_on_this_floor_are_updated():
    items = Items()

    # Items on level 0:
    sword = Item(Point(1, 1, 0), name="sword")
    hat = Item(Point(1, 1, 0), name="hat")
    # Items on level 1:
    boots = Item(Point(1, 1, 1), name="boots")

    items.add(sword)
    items.add(hat)
    items.add(boots)

    # When... the items are updated on level 0
    items._delete_all_items_on_floor(level=0)

    assert_that(items.get_as_list()).is_not_none() \
        .is_length(1).is_equal_to([boots])


def test_adding_item_at_position_sets_item_position():
    items = Items()

    # Items on level 0:
    sword = Item(Point(1, 1, 0), name="sword")

    items.add_item_to_position(item=sword, point=Point(3, 3, 0))

    assert_that(sword.position).is_equal_to(Point(3, 3, 0))
