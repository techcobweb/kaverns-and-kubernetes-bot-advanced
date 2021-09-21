
import unittest
import roguebot
import pytest
from roguebot.bot import Bot
from roguebot.state.item import Item, Items
from roguebot.state.entity import Entity, Entities
from roguebot.state.dungeon_map import DungeonMap
from assertpy import assert_that
from unittest.mock import Mock
from tests.state.dungeon_draw import *
from roguebot.state.state import State


def test_state_is_empty_when_created():
    state = State()
    entities = Entities()
    assert_that(len(entities)).is_equal_to(0)
    assert_that(len(state.entities)).is_equal_to(0)


def test_state_creatable_with_items_and_entities():
    entities = Entities()
    items = Items()
    state = State(entities=entities, items=items)
    assert_that(state.items).is_equal_to(items)
    assert_that(state.entities).is_equal_to(entities)


def test_can_update_items_with_my_position():
    state: State = State()

    entities = Entities()
    state._entities = entities

    state.my_entity_id = 'aaa'
    me = Entity(char='A', name='mike',
                identifier='aaa', position=Point(1, 2, 3))
    entities.add(me)

    mock_items = Mock(return_value=me)
    state._items = mock_items
    mock_items.update_items = Mock()
    test_items_data = "something made up for testing"

    # When
    state.update_items(test_items_data)

    # Then
    mock_items.update_items.assert_called_with(
        test_items_data, Point(1, 2, 3))


class TestState(unittest.TestCase):

    def test_can_set_and_get_dungeon_map(self):
        state = State()
        assert_that(state.dungeon_map).is_none()

        dungeon_picture = """
            ----------- level z=0 :
            ####
            #  #
            ####
            -----------
            """
        state.dungeon_map = get_dungeon_from_picture(dungeon_picture)
        assert_that(state.dungeon_map).is_not_none()

    def test_state_has_a_message_queue(self):
        state = State()
        state.messages.append("first")
        state.messages.append("second")
        assert_that(state.messages.pop(0)).is_equal_to("first")
        assert_that(state.messages.pop(0)).is_equal_to("second")
