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
from roguebot.goals.attack_goal import AttackEntity


@pytest.fixture
def me() -> Entity:
    return Entity(char='@',
                  name='myself',
                  position=Point(1, 1, 0),
                  identifier='myId')


@pytest.fixture
def goblin() -> Entity:
    return Entity(char='G',
                  name="gobbo",
                  position=Point(1, 2, 0),
                  identifier='gob1')


@pytest.fixture
def unicorn() -> Entity:
    """
    A unicorn, miles outside of the dungeon, so no route to it.
    """
    return Entity(char='U',
                  name="unicorn",
                  position=Point(99, 99, 99),
                  identifier='uni1')


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


def test_can_set_target_entity_id_and_name_on_construction():
    goal = AttackEntity("fredID", "fred")
    assert_that(goal._target_entity_name).is_equal_to("fred")
    assert_that(goal._target_entity_id).is_equal_to("fredID")


def test_str_holds_name_and_id():
    goal = AttackEntity("fredID", "fred")
    assert_that(str(goal)).contains(
        "AttackEntity").contains("fred").contains("fredID")


def test_targets_only_enemy(me_in_no_item_state: State,
                            me: Entity,
                            goblin: Entity):
    state = me_in_no_item_state
    # Add one target
    state.entities.add(goblin)

    goal = AttackEntity()
    got_target = goal.acquire_target(me=me, state=state)

    assert_that(got_target).is_true()
    assert_that(goal.target_entity_id).is_equal_to(goblin.entity_id)
    assert_that(goal._target_entity_name).is_equal_to(goblin.name)


def test_no_targets_doesnt_find_any(me_in_no_item_state: State,
                                    me: Entity):
    state = me_in_no_item_state

    goal = AttackEntity()
    got_target = goal.acquire_target(me=me, state=state)

    assert_that(got_target).is_false()


def test_enemy_score_entity_out_of_reach(me_in_no_item_state: State,
                                         me: Entity,
                                         unicorn: Entity):
    state = me_in_no_item_state

    state._entities.add(unicorn)

    goal = AttackEntity()
    got_target = goal.acquire_target(me=me, state=state)
    score = goal.score_enemy(enemy=unicorn, me=me, state=state)

    assert_that(score).is_equal_to(-5000)
    assert_that(got_target).is_false()


def test_close_enemy_has_high_score(me_in_no_item_state: State,
                                    me: Entity,
                                    goblin):
    state = me_in_no_item_state
    # The goblin is really close to 'me'
    state._entities.add(goblin)
    goal = AttackEntity()

    score = goal.score_enemy(enemy=goblin, me=me, state=state)

    # Expecting a big score from this immediate threat.
    assert_that(score).is_greater_than(400)


def test_targetted_enemy_dies_stops_goal(me_in_no_item_state: State,
                                         me: Entity,
                                         goblin: Entity):
    state = me_in_no_item_state
    state._entities.add(goblin)
    goal = AttackEntity()
    goals = [goal]
    actions = []

    # Acquire the target
    goal.acquire_target(me, state)

    # Now remove the target from the state completely.
    state._entities.delete_by_id(goblin.entity_id)

    goal.move_towards_enemy(state, me, actions, goals)

    # It should have de-queued itself from the goals stack.
    assert_that(len(goals)).is_equal_to(0)
