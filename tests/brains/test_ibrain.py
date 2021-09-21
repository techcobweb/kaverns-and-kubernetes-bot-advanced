

import unittest
from assertpy import assert_that
from roguebot.brains.ibrain import IBrain


def test_ibrain_can_set_and_get_status():
    class TestBrain(IBrain):
        def decide_actions(self, state):
                return super().decide_actions(state)

    made_up_status = {"something": "made up"}
    brain = TestBrain()
    brain.status_summary = made_up_status

    summary = brain.status_summary
    assert_that(summary).is_equal_to(made_up_status)
