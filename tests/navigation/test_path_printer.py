import unittest
import roguebot
import pytest
import logging

from roguebot.navigation.path import PathFinder
from abc import ABC, abstractmethod
from roguebot.action import Action, MoveAction, TakeAction
from roguebot.state.state import State
from roguebot.navigation.path_printer import *
from tests.state.dungeon_draw import *
from roguebot.action import *
from roguebot.state.item import Item, Items
from assertpy import assert_that
from roguebot.state.entity import Entities, Entity
from roguebot.navigation.direction import Direction
from roguebot.navigation.point import Point
from roguebot.state.dungeon_map import DungeonMap
from enum import Enum


@pytest.fixture
def path_printer() -> PathPrinter:
    return PathPrinter()


@pytest.fixture
def small_room() -> DungeonMap:
    picture = """
        ----------- level z=0 :
        ######
        #    #
        #    #
        #    #
        ######
        -----------
        """
    dungeon = get_dungeon_from_picture(picture)
    return dungeon


@pytest.fixture
def dagger() -> Item:
    return Item(name="dagger")


def test_can_print_dungeon(small_room, path_printer):
    dungeon = small_room
    state = State()
    state.dungeon_map = dungeon

    rendered_map: str = path_printer.render_path(state=state, path=[Point(
        2, 2, 0)], only_show_floor=None, me_point=Point(1, 1, 0))

    assert_that(rendered_map).is_not_none()


def test_can_print_dungeon_contains_my_position(small_room, path_printer):
    dungeon = small_room

    state = State()
    state.dungeon_map = dungeon
    rendered_map: str = path_printer.render_path(state=state, path=[Point(
        2, 2, 0)], only_show_floor=None, me_point=Point(1, 1, 0))

    # Check my position is marked.
    assert_that(rendered_map).contains('X')


def test_dot_cells_are_shown_as_spaces(small_room, path_printer):
    dungeon = small_room

    # Normally, a dot glyph is used for empty dungeon space.
    cell_with_dot_glyph = Cell('.', is_walkable=True)
    dungeon.set_cell(Point(2, 3, 0), cell_with_dot_glyph)

    state = State()
    state.dungeon_map = dungeon
    rendered_map: str = path_printer.render_path(state=state, path=[Point(
        2, 2, 0)], only_show_floor=None, me_point=Point(1, 1, 0))

    # Only one path point given, so should only be one 'dot'
    assert_that(rendered_map.count('.')).is_equal_to(1)


def test_items_are_shown_as_splats(small_room, path_printer, dagger):
    dungeon = small_room
    state = State()
    state.dungeon_map = dungeon

    dagger.position = Point(3, 1, 0)
    state.items.add(dagger)

    rendered_map: str = path_printer.render_path(state=state, path=[Point(
        2, 2, 0)], only_show_floor=None, me_point=Point(1, 1, 0))

    # Only one path point given, so should only be one 'dot'
    assert_that(rendered_map.count('*')).is_equal_to(1)
