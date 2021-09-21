
import unittest
from roguebot.goals.goal import Goal
from assertpy import assert_that
from unittest.mock import Mock
from unittest import IsolatedAsyncioTestCase


def test_goal_complete_pops_off_goal_stack() -> None:
    goal1 = Goal()
    goal2 = Goal()
    goal_stack = [goal1, goal2]

    goal2.goal_completed(goal_stack)

    assert_that(goal_stack).is_length(1).is_equal_to([goal1])


def test_goal_renders_to_a_string_ok() -> None:
    goal1 = Goal()
    s = str(goal1)
    assert_that(s).is_equal_to("Goal")


def test_goal_subclass_renders_to_a_string_ok() -> None:
    class SubGoal(Goal):
        """A subclass of Goal"""

    goal1 = SubGoal()
    s = str(goal1)
    assert_that(s).is_equal_to("SubGoal")
