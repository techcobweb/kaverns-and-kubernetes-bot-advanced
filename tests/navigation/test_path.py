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


logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def path_finder() -> PathFinder:
    return PathFinder()


@pytest.fixture
def path_printer() -> PathPrinter:
    return PathPrinter()


@pytest.fixture
def empty_state() -> State:
    state = State()


@pytest.fixture
def sword() -> Item:
    return Item(position=Point(0, 0, 0), name="sword",
                edible=False, wieldable=True, wearable=False, damage=6)


@pytest.fixture
def killer_entity(sword) -> Entity:
    killer = Entity("X", "killer", Point(1, 2, 0), identifier="killerEntity1", alive=True, inventory=[sword],
                    current_weapon=sword)
    return killer


@pytest.fixture
def rich_entity() -> Entity:
    return Entity("X", "ritch", Point(1, 2, 0), identifier="ritch1", alive=True, inventory=[],
                  current_weapon=None)


@pytest.fixture
def peaceful_entity() -> Entity:
    return Entity("X", "hippie", Point(1, 2, 0), identifier="hippie1", alive=True, inventory=[],
                  current_weapon=None)


@pytest.fixture
def small_room() -> State:
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
    state = State()
    state.entities = Entities()
    state.items = Items()
    state.dungeon_map = dungeon
    return state


@pytest.fixture
def two_rooms() -> State:
    picture = """
        ----------- level z=0 :
        ######
        #    #
        #    #
        #    #
        #### #
        #    #
        #    #
        #    #
        ######
        -----------
        """
    dungeon = get_dungeon_from_picture(picture)
    state = State()
    state.entities = Entities()
    state.items = Items()
    state.dungeon_map = dungeon
    return state


@pytest.fixture
def two_rooms_gateway_in_between() -> State:
    picture = """
        ----------- level z=0 :
        ######
        #    #
        #    #
        #    #
        ####O#
        #    #
        #    #
        #    #
        ######
        -----------
        """
    dungeon = get_dungeon_from_picture(picture)
    state = State()
    state.entities = Entities()
    state.items = Items()
    state.dungeon_map = dungeon
    return state


@pytest.fixture
def two_rooms_gateway_maze() -> State:
    picture = """
        ----------- level z=0 :
        ######
        # O  #
        #   O#
        # O  #
        #### #
        #    #
        # OOO#
        #    #
        ######
        -----------
        """
    dungeon = get_dungeon_from_picture(picture)
    state = State()
    state.entities = Entities()
    state.items = Items()
    state.dungeon_map = dungeon
    return state


@pytest.fixture
def two_level_dungeon() -> State:
    """ A dungeon which can force movement from one
    level to the other, then back to the original level.
    """
    picture = """
    ----------- level z=0 : origin is top-left
    ######
    #    #
    #    #
    # >  #
    ######
    #    #
    # ####
    #  > #
    ######
    ----------- level z=1 : origin is top-left
    ######
    #    #
    #  # #
    # <# #
    #### #
    #    #
    #    #
    #  < #
    ######
    -----------
    """
    dungeon = get_dungeon_from_picture(picture)
    state = State()
    state.entities = Entities()
    state.items = Items()
    state.dungeon_map = dungeon
    return state


def test_can_set_and_get_attempt_limit(path_finder):
    path_finder.attempt_limit = 20
    assert_that(path_finder.attempt_limit).is_equal_to(20)


def test_point_distance_score_on_same_point(path_finder):
    score = path_finder.score_point_distance(
        Point(1, 1, 1), Point(1, 1, 1))
    assert_that(score).is_equal_to(0)


def test_point_distance_score_on_one_higher_y(path_finder):
    score = path_finder.score_point_distance(
        Point(1, 1, 1), Point(1, 2, 1))
    assert_that(score).is_equal_to(1)


def test_point_distance_score_on_one_higher_x(path_finder):
    score = path_finder.score_point_distance(
        Point(1, 1, 1), Point(2, 1, 1))
    assert_that(score).is_equal_to(1)


def test_point_distance_score_on_one_higher_z(path_finder):
    score = path_finder.score_point_distance(
        Point(1, 1, 1), Point(1, 1, 2))
    assert_that(score).is_equal_to(
        PathFinder.DIFFERENT_LEVEL_DISTANCE_SCORE)


def test_point_distance_score_on_one_lower_y(path_finder):
    score = path_finder.score_point_distance(
        Point(1, 1, 1), Point(1, 0, 1))
    assert_that(score).is_equal_to(1)


def test_point_distance_score_on_one_lower_x(path_finder):
    score = path_finder.score_point_distance(
        Point(1, 1, 1), Point(0, 1, 1))
    assert_that(score).is_equal_to(1)


def test_point_distance_score_on_one_lower_z(path_finder):
    score = path_finder.score_point_distance(
        Point(1, 1, 1), Point(1, 1, 0))
    assert_that(score).is_equal_to(
        PathFinder.DIFFERENT_LEVEL_DISTANCE_SCORE)


def test_find_path_between_same_points(path_finder, empty_state: State):
    # When ...
    path = path_finder.find_path(
        Point(0, 0, 0), Point(0, 0, 0), empty_state)
    # Then ...
    assert_that(path).is_length(1) \
        .contains(Point(0, 0, 0))


def test_find_path_between_neighbour_points(path_finder, small_room: State):
    # When ...
    path = path_finder.find_path(
        Point(1, 1, 0), Point(1, 2, 0), small_room)
    # Then ...
    assert_that(path).is_length(2) \
        .contains(Point(1, 1, 0)) \
        .contains(Point(1, 2, 0))


def test_find_path_between_further_away_points(path_finder, small_room: State):
    # When ...
    path = path_finder.find_path(
        Point(1, 1, 0), Point(2, 2, 0), small_room)
    # Then ...
    assert_that(path).is_length(3) \
        .contains(Point(1, 1, 0)) \
        .contains(Point(2, 2, 0))


def test_find_path_between_even_further_away_points(path_finder, path_printer, small_room: State):
    # When ...
    path = path_finder.find_path(
        Point(1, 1, 0), Point(3, 3, 0), small_room)
    # Then ...
    print(path_printer.render_path(small_room, path))
    assert_that(path).is_length(5) \
        .contains(Point(1, 1, 0)) \
        .contains(Point(3, 3, 0))


def test_gives_up_if_target_point_unreachable(path_finder, path_printer, small_room: State):
    # When ...
    path = path_finder.find_path(
        Point(1, 1, 0), Point(10, 10, 0), small_room)
    # Then ...
    print(path_printer.render_path(small_room, path))
    assert_that(path).is_none()


def test_find_path_between_two_rooms(path_finder, path_printer, two_rooms: State):
    # When ...
    path = path_finder.find_path(
        Point(1, 1, 0), Point(1, 6, 0), two_rooms)

    print(path_printer.render_path(two_rooms, path))
    # Then ...
    assert_that(path).is_length(9) \
        .contains(Point(1, 1, 0)) \
        .contains(Point(1, 6, 0))


def test_find_path_between_two_rooms(path_finder, path_printer, two_rooms: State):
    # When ...
    from_point = Point(1, 6, 0)
    to_point = Point(1, 1, 0)
    path = path_finder.find_path(
        from_point, to_point, two_rooms)

    print(path_printer.render_path(two_rooms, path))
    # Then ...
    assert_that(path).is_length(12) \
        .contains(Point(1, 1, 0)) \
        .contains(Point(1, 6, 0))


def test_find_path_between_two_levels(path_finder, path_printer, two_level_dungeon: State):
    # When ...
    from_point = Point(1, 1, 0)
    to_point = Point(4, 5, 0)
    path = path_finder.find_path(
        from_point, to_point, two_level_dungeon)

    print(path_printer.render_path(two_level_dungeon, path))
    # Then ...
    assert_that(path) \
        .contains(Point(1, 1, 0)) \
        .contains(Point(4, 5, 0))
    assert_that(len(path)).is_greater_than(23) \
        .is_less_than(30)


def test_find_path_which_is_too_complex_gives_up(path_finder, path_printer, two_rooms: State):
    # When ...
    from_point = Point(1, 6, 0)
    to_point = Point(1, 1, 0)
    path_finder.attempt_limit = 4

    path = path_finder.find_path(
        from_point, to_point, two_rooms)

    print(path_printer.render_path(two_rooms, path))
    # Then ...
    assert_that(path).is_none()


def test_find_path_between_two_rooms_avoiding_entities(

        path_finder,
        path_printer,
        two_rooms: State,
        killer_entity: Entity,
        peaceful_entity: Entity,
        rich_entity: Entity):

    # Given ...
    killer_entity.position = Point(2, 1, 0)
    two_rooms.entities.add(killer_entity)
    peaceful_entity.position = Point(2, 6, 0)
    two_rooms.entities.add(peaceful_entity)
    rich_entity.position = Point(3, 3, 0)
    two_rooms.entities.add(rich_entity)

    # When ...
    path = path_finder.find_path(
        Point(1, 1, 0), Point(1, 6, 0), two_rooms)

    print(path_printer.render_path(two_rooms, path))
    # Then ...
    assert_that(path).is_length(12) \
        .contains(Point(1, 1, 0)) \
        .contains(Point(1, 6, 0)) \
        .does_not_contain(Point(2, 1, 0)) \
        .does_not_contain(Point(2, 6, 0)) \
        .does_not_contain(Point(3, 3, 0))


def test_find_path_between_two_rooms_divided_by_gateway_no_route(path_finder, path_printer, two_rooms_gateway_in_between: State):
    # When ...
    state = two_rooms_gateway_in_between
    from_point = Point(1, 6, 0)
    to_point = Point(1, 1, 0)
    path = path_finder.find_path(
        from_point, to_point, state)

    print(path_printer.render_path(state, path))
    # Then ...
    assert_that(path).is_none()


def test_find_path_around_gateway_infested_route(path_finder, path_printer, two_rooms_gateway_maze: State):
    # When ...
    state = two_rooms_gateway_maze
    from_point = Point(1, 1, 0)
    to_point = Point(4, 7, 0)
    path = path_finder.find_path(
        from_point, to_point, state)

    print(path_printer.render_path(state, path))
    # Then ...
    assert_that(path).is_length(16)


def test_find_path_to_gateway_point(path_finder, path_printer, two_rooms_gateway_maze: State):
    # When ...
    state = two_rooms_gateway_maze
    from_point = Point(1, 1, 0)
    to_point = Point(2, 1, 0)
    path = path_finder.find_path(
        from_point, to_point, state)

    print(path_printer.render_path(state, path))
    # Then ...
    assert_that(path).is_length(2)


if __name__ == '__main__':
    unittest.main()
