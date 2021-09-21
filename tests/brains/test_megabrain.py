

import unittest
import roguebot
import pytest

from roguebot.state.dungeon_map import DungeonMap
from roguebot.brains.ibrain import IBrain
from roguebot.brains.item_handling_brain import ItemHandlingBrain
from roguebot.navigation.point import Point
from roguebot.navigation.direction import Direction
from roguebot.state.entity import Entities, Entity
from assertpy import assert_that
from roguebot.state.item import Item, Items
from roguebot.action import *
from tests.state.dungeon_draw import *
from roguebot.state.state import State
from roguebot.action import Action, MoveAction, TakeAction
from roguebot.brains.megabrain import MegaBrain


@pytest.fixture
def empty_brain() -> MegaBrain:
    return MegaBrain()


@pytest.fixture
def state_with_no_items() -> State:
    state = State()
    state.items = Items()
    return state


@pytest.fixture
def dagger() -> Item:
    return Item(name='dagger', wieldable=True)


@pytest.fixture
def state_with_one_item(dagger) -> State:
    state = State()
    state.items = Items()
    state.items.add(dagger)
    return state


def test_megabrain_can_be_created(empty_brain) -> None:
    # The fact we got here says a mega-brain can be created.
    pass


def test_megabrain_create_goal_creates_a_choose_goal_goal(empty_brain: MegaBrain) -> None:
    empty_brain.create_goal()
    assert_that(empty_brain._goals).is_length(1)


def test_monitor_items_available_no_goals_added_if_item_count_does_not_change(empty_brain: MegaBrain, state_with_no_items: State) -> None:
    brain = empty_brain
    state = state_with_no_items
    initial_goal_count = len(brain._goals)

    brain._monitor_new_items_available(state)

    after_goal_count = len(brain._goals)
    assert_that(after_goal_count).is_equal_to(initial_goal_count)


def test_monitor_items_adds_goals_if_item_count_changes(empty_brain: MegaBrain, state_with_no_items: State, state_with_one_item: State) -> None:
    brain = empty_brain
    initial_goal_count = len(brain._goals)

    brain._monitor_new_items_available(state_with_no_items)
    brain._monitor_new_items_available(state_with_one_item)

    after_goal_count = len(brain._goals)
    assert_that(after_goal_count).is_equal_to(initial_goal_count+2)
