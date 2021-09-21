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
from roguebot.goals.explore_goal import ExploreGoal


@pytest.fixture
def small_room_state() -> State:
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
    state.dungeon_map = dungeon
    return state


def test_explore_goal_completes_after_one_hundred_turns(small_room_state) -> None:

    me = Entity(char='@', name='dilbert',
                position=Point(1, 1, 0), identifier="nerd1")
    small_room_state.entities.add(me)
    small_room_state.my_entity_id = "nerd1"
    goal = ExploreGoal()
    goals = [goal]
    for i in range(102):
        goal.decide_actions(me=me, state=small_room_state, goals=goals)
    assert_that(goals).is_empty()
