

import unittest
import roguebot
import pytest

from roguebot.state.dungeon_map import DungeonMap
from roguebot.brains.ibrain import IBrain
from roguebot.brains.brain import GoalDrivenBrain
from roguebot.navigation.point import Point
from roguebot.navigation.direction import Direction
from roguebot.state.entity import Entities, Entity
from assertpy import assert_that
from roguebot.state.item import Item, Items
from roguebot.action import *
from tests.state.dungeon_draw import *
from roguebot.state.state import State
from roguebot.action import Action, MoveAction, TakeAction
from abc import ABC, abstractmethod


@pytest.fixture
def sword() -> Item:
    return Item(position=Point(0, 0, 0), name="sword",
                edible=False, wieldable=True, wearable=False, damage=6)


@pytest.fixture
def dagger() -> Item:
    return Item(position=Point(0, 0, 0), name="dagger",
                edible=False, wieldable=True, wearable=False, damage=3)


def test_brain_max_moves_per_turn_defaults_to_1() -> None:
    brain = GoalDrivenBrain()
    assert_that(brain.max_actions_per_turn).is_equal_to(1)


def test_brain_max_moves_per_turn_can_be_set_and_got_back() -> None:
    brain = GoalDrivenBrain()
    assert_that(brain.max_actions_per_turn).is_equal_to(1)
    brain.max_actions_per_turn = 2
    assert_that(brain.max_actions_per_turn).is_equal_to(2)


def test_clear_brain_flushes_goal_list() -> None:
    brain = GoalDrivenBrain()
    brain._goals.append("something")
    brain.clear()
    assert_that(brain._goals).is_empty()


class BaseBrainTest(unittest.TestCase):

    def get_entities(self, my_position: Point = Point(1, 1, 0), my_entity_id="fredID") -> Entities:
        me = Entity(char="@", name="fred",
                    position=my_position, identifier=my_entity_id, alive=True, inventory=[])
        print("me:"+str(me))
        entities = Entities()
        entities.add(me)

        return entities

    def setup_test_data(self,
                        dungeon_picture: str,
                        entrance_point=Point(99, 99, 99),
                        my_position=Point(1, 1, 0)
                        ) -> (State, IBrain):

        state = State()
        print("state before setup:{}".format(state))
        state.dungeon_map = get_dungeon_from_picture(
            dungeon_picture, entrance=entrance_point)

        print("state after dungegon loaded:{}".format(state))

        state.my_entity_id = "fredID"
        entities = self.get_entities(
            my_position=my_position, my_entity_id=state.my_entity_id)
        state.entities = entities

        print("state after entities loaded:{}".format(state))

        state.items = Items()

        print("state after items loaded:{}".format(state))

        brain = self.create_brain()
        return (state, brain)

    def create_brain(self) -> IBrain:
        return GoalDrivenBrain()

    def get_brain_decisions(self, dungeon_picture: str, entrance_point: Point = Point(99, 99, 99), my_position: Point = Point(1, 1, 0)) -> (State, [Action]):

        (state, brain) = self.setup_test_data(
            dungeon_picture, entrance_point, my_position)

        actions = brain.decide_actions(state)

        return (state, actions)


class TestGoalDrivenBrain(BaseBrainTest):

    def create_brain(self) -> IBrain:
        return GoalDrivenBrain()

    def test_moves_to_walkable_area_in_the_east(self):
        """ Small room, entrance on the left. Start at the entrance.
        Only one way to move: East."""
        picture = """
            ----------- level z=0 :
            ####
            #  #
            ####
            -----------
            """
        (state, actions) = self.get_brain_decisions(
            picture, entrance_point=Point(1, 1, 0), my_position=Point(1, 1, 0))

        assert_that(actions).is_length(1)
        action = actions.pop()
        assert_that(action.action_code).is_equal_to(ActionCode.MOVE)
        assert_that(action.direction).is_equal_to(Direction.EAST)

    def test_moves_to_walkable_area_in_the_west(self):
        """ Small room, entrance on the right. Start on the right.
        there is only one way to move. West"""
        picture = """
            ----------- level z=0 :
            ####
            #  #
            ####
            -----------
            """
        (state, actions) = self.get_brain_decisions(
            picture, entrance_point=Point(2, 1, 0), my_position=Point(2, 1, 0))

        assert_that(actions).is_length(1)
        action = actions.pop()
        assert_that(action.action_code).is_equal_to(ActionCode.MOVE)
        assert_that(action.direction).is_equal_to(Direction.WEST)

    def test_moves_to_walkable_area_in_the_south(self):
        """ Small room, no entrance. Start on top.
        there is only one way to move. South"""
        picture = """
            ----------- level z=0 :
            ###
            # #
            # #
            ###
            -----------
            """
        (state, actions) = self.get_brain_decisions(
            picture, entrance_point=Point(1, 1, 0), my_position=Point(1, 1, 0))

        assert_that(actions).is_length(1)
        action = actions.pop()
        assert_that(action.action_code).is_equal_to(ActionCode.MOVE)
        assert_that(action.direction).is_equal_to(Direction.SOUTH)

    def test_moves_to_walkable_area_in_the_north(self):
        """ Small room, no entrance. Start on botttom.
        there is only one way to move. North"""
        picture = """
            ----------- level z=0 :
            ###
            # #
            # #
            ###
            -----------
            """
        (state, actions) = self.get_brain_decisions(
            picture, entrance_point=Point(1, 2, 0), my_position=Point(1, 2, 0))

        assert_that(actions).is_length(1)
        action = actions.pop()
        assert_that(action.action_code).is_equal_to(ActionCode.MOVE)
        assert_that(action.direction).is_equal_to(Direction.NORTH)

    def test_moves_up_stairs(self):
        picture = """
            ----------- level z=0 : top of dungeon: origin is top-left corner.
            ###
            #>#
            ###
            ----------- level z=1: one level up:
            ###
            #<#
            ###
            -----------
            """
        (state, actions) = self.get_brain_decisions(
            picture, my_position=Point(1, 1, 1))

        assert_that(actions).is_length(1)
        action = actions.pop()
        assert_that(action.action_code).is_equal_to(ActionCode.MOVE)
        assert_that(action.direction).is_equal_to(Direction.UP)

    def test_moves_down_stairs(self):
        picture = """
            ----------- level z=0 : top of dungeon: origin is top-left corner.
            ###
            #>#
            ###
            ----------- level z=1: one level up:
            ###
            #<#
            ###
            -----------
            """
        (state, actions) = self.get_brain_decisions(
            picture, my_position=Point(1, 1, 0))

        assert_that(actions).is_length(1)
        action = actions.pop()
        assert_that(action.action_code).is_equal_to(ActionCode.MOVE)
        assert_that(action.direction).is_equal_to(Direction.DOWN)

    def test_nowhere_to_go_gives_no_actions(self):
        picture = """
            ----------- level z=0 :
            ###
            # #
            ###
            -----------
            """
        (state, actions) = self.get_brain_decisions(
            picture, my_position=Point(1, 1, 0))

        assert_that(actions).is_length(0)

    def testCanExploreASmallEmptyRoom(self):
        """ If we have a 2x2 room, and move 4 times, we should
        have explored all cells in that room.
        """
        picture = """
            ----------- level z=0 :
            ####
            #  #
            #  #
            ####
            -----------
            """
        max_moves_to_make = 3

        points_visited = self.explore_dungeon(picture, max_moves_to_make)

        assert_that(points_visited).contains(Point(2, 2, 0))
        assert_that(points_visited).contains(Point(1, 2, 0))
        assert_that(points_visited).contains(Point(2, 1, 0))
        assert_that(points_visited).contains(Point(1, 1, 0))

    def explore_dungeon(self, picture: str, max_moves_to_make: int) -> [Point]:

        (state, brain) = self.setup_test_data(
            picture, entrance_point=Point(1, 1, 0), my_position=Point(1, 1, 0))

        me = state.find_my_entity()
        points_visited = {me.position}

        for _ in range(0, max_moves_to_make):
            actions = brain.decide_actions(state)
            for action in actions:
                if action.action_code == ActionCode.MOVE:
                    dir = action.direction
                    me.position = me.position.get_neighbour(dir)
                    points_visited.add(me.position)

        return points_visited

    def testCanExploreATwoFloorHouse(self):
        """ If we have a 2x2 room, and move 4 times, we should have
        explored all cells in that room.
        """
        picture = """
            ----------- level z=0 : top of dungeon:
            ####
            # >#
            #  #
            ####
            ----------- level z=1: one level down:
            ####
            # <#
            #  #
            ####
            -----------
            """
        max_moves_to_make = 15

        points_visited = self.explore_dungeon(picture, max_moves_to_make)

        assert_that(points_visited).contains(Point(1, 1, 0))
        assert_that(points_visited).contains(Point(1, 2, 0))
        assert_that(points_visited).contains(Point(2, 2, 0))
        assert_that(points_visited).contains(Point(2, 1, 0))
        assert_that(points_visited).contains(Point(1, 1, 1))
        assert_that(points_visited).contains(Point(1, 2, 1))
        assert_that(points_visited).contains(Point(2, 2, 1))
        assert_that(points_visited).contains(Point(2, 1, 1))


if __name__ == '__main__':
    unittest.main()
