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
from roguebot.goals.seek_item_goal import SeekItemGoal


@pytest.fixture
def me() -> Entity:
    return Entity(char='@', name='myself', position=Point(1, 1, 0), identifier='myId')


@pytest.fixture
def dust() -> Item:
    """A useless item"""
    return Item(position=Point(2, 3, 0), name='dust')


@pytest.fixture
def banana() -> Item:
    """A yummy item"""
    return Item(position=Point(2, 2, 0), name='banana', edible=True)


@pytest.fixture
def hat() -> Item:
    """A jazzy head wrapping"""
    return Item(position=Point(3, 2, 0), name='hat', wearable=True)


@pytest.fixture
def thors_hammer() -> Item:
    """It exists, does huge damage, but it's well out of reach, so should be ignored."""
    return Item(position=Point(99, 99, 99), name="thor's hammer", wieldable=True, damage=10000)


@pytest.fixture
def pike() -> Item:
    """A pointy metal-tipped stick"""
    return Item(position=Point(3, 3, 0), name='pike', wieldable=True, damage=5)


@pytest.fixture
def scissors() -> Item:
    """A crappy weapon, but it does work a bit."""
    return Item(position=Point(3, 3, 0), name='scissors', wieldable=True, damage=1)


@pytest.fixture
def me_in_no_item_state(me) -> State:
    state = State()

    state.entities.add(me)
    state.my_entity_id = me.identifier

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
    state.dungeon_map = dungeon
    return state


@pytest.fixture
def one_banana_state(me_in_no_item_state, banana) -> State:
    state = me_in_no_item_state
    state.items.add(banana)
    return state


@pytest.fixture
def one_dust_state(me_in_no_item_state, dust) -> State:
    state = me_in_no_item_state
    state.items.add(dust)
    return state


def test_str_renders_target_point_and_item_name():
    goal = SeekItemGoal(point=Point(1, 2, 3), target_item_name="banana")
    assert_that(str(goal)).contains(str(Point(1, 2, 3))).contains(
        "banana").contains('SeekItemGoal')


def test_acquires_edible_target_item_available(me, one_banana_state, banana):
    state = one_banana_state
    goal = SeekItemGoal()

    score = goal.score_item(me, banana, state)
    acquired_target_ok = goal.acquire_target(me, state)

    assert_that(acquired_target_ok).is_true()
    assert_that(goal._target_item_name).is_equal_to(banana.name)
    assert_that(goal._target_point).is_equal_to(banana.position)
    assert_that(score).is_equal_to(294)


def test_doesnt_bother_targetting_useless_items(me, one_dust_state, dust):
    state = one_dust_state
    goal = SeekItemGoal()
    state.items.add(dust)

    score = goal.score_item(me, dust, state)
    acquired_target_ok = goal.acquire_target(me, state)

    assert_that(acquired_target_ok).is_false()
    assert_that(goal._target_item_name).is_none()
    assert_that(goal._target_point).is_none()
    assert_that(score).is_equal_to(0)


def test_doesnt_bother_targetting_unreachable_items(me, one_dust_state, thors_hammer):
    state = one_dust_state
    goal = SeekItemGoal()
    state.items.add(thors_hammer)

    score = goal.score_item(me, thors_hammer, state)
    acquired_target_ok = goal.acquire_target(me, state)

    assert_that(acquired_target_ok).is_false()
    assert_that(goal._target_item_name).is_none()
    assert_that(goal._target_point).is_none()
    assert_that(score).is_less_than(0)


def test_can_select_wearable_item(me, me_in_no_item_state, hat):
    state = me_in_no_item_state
    state.items.add(hat)
    goal = SeekItemGoal()

    score = goal.score_item(me, hat, state)
    acquired_target_ok = goal.acquire_target(me, state)

    assert_that(acquired_target_ok).is_true()
    assert_that(goal._target_item_name).is_equal_to(hat.name)
    assert_that(goal._target_point).is_equal_to(hat.position)
    assert_that(score).is_equal_to(292)


def test_can_select_wieldable_item(me, me_in_no_item_state, pike):
    state = me_in_no_item_state
    state.items.add(pike)
    goal = SeekItemGoal()

    score = goal.score_item(me, pike, state)
    acquired_target_ok = goal.acquire_target(me, state)

    assert_that(acquired_target_ok).is_true()
    assert_that(goal._target_item_name).is_equal_to(pike.name)
    assert_that(goal._target_point).is_equal_to(pike.position)
    assert_that(score).is_equal_to(390)


def test_scores_wieldable_item_higher_when_better_than_already_got(me, me_in_no_item_state, pike, scissors):
    state = me_in_no_item_state

    # The pike is available in the world.
    state.items.add(pike)

    # We are holding scissors.
    me.inventory.append(scissors)
    me.current_weapon = scissors

    goal = SeekItemGoal()

    # When we work out the score...
    score = goal.score_item(me, pike, state)

    # It should be big,
    assert_that(score).is_equal_to(390)


def test_scores_wieldable_item_higher_when_worse_than_already_got(me, me_in_no_item_state, pike, scissors):
    state = me_in_no_item_state

    # The scissors is available in the world.
    state.items.add(scissors)

    # We are holding pike.
    me.inventory.append(pike)
    me.current_weapon = pike

    goal = SeekItemGoal()

    # When we work out the score...
    score = goal.score_item(me, scissors, state)

    # It should be big,
    assert_that(score).is_equal_to(240)


def test_selects_weapons_over_food_and_clothing(me, me_in_no_item_state, pike, scissors, dust, banana, hat):
    state = me_in_no_item_state
    state.items.add(pike)
    state.items.add(scissors)
    state.items.add(dust)
    state.items.add(banana)
    state.items.add(hat)
    goal = SeekItemGoal()

    acquired_target_ok = goal.acquire_target(me, state)

    assert_that(acquired_target_ok).is_true()
    assert_that(goal._target_item_name).is_equal_to(pike.name)
    assert_that(goal._target_point).is_equal_to(pike.position)


def test_notices_targetted_item_is_missing(me, me_in_no_item_state, banana):
    state = me_in_no_item_state

    # Target the banana...
    state.items.add(banana)
    goal = SeekItemGoal()
    acquired_target_ok = goal.acquire_target(me, state)

    # It is still there.
    assert_that(goal.is_item_still_there(state)).is_true()

    # Now remove the banana
    state.items.delete(banana)

    # Should notice it's moved.
    assert_that(goal.is_item_still_there(state)).is_false()


def test_no_items_to_seek_pops_goal_off_stack():
    goal = SeekItemGoal()
    goals = [goal]
    goal.no_items_to_seek(goals)

    assert_that(goals).is_empty()

def test_when_reach_destination_choose_another_goal():
    goal = SeekItemGoal()
    goals = [goal]

    goal.destination_reached(goals)

    assert_that(len(goals)).is_equal_to(1)
    assert_that(str(goals[0])).contains("SeekItemGoal")