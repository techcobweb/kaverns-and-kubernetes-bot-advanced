"""Goals are things which are worked towards, and sometimes achieved.

They can complete un-finished too.
"""

import logging

from ..state.entity import Entity
from ..state.state import State
from ..action import Action
from ..navigation.path_printer import PathPrinter


class Goal():
    """A basic goal. Does nothing.

    Each subclass of this goal houses different aimed at achieving the goal.
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._path_printer = PathPrinter()

    def __str__(self):
        """
        Subclasses can at least get their class-name rendered as a string.
        """
        return str(type(self).__name__)

    def decide_actions(self, me: Entity, state: State, goals) -> [Action]:
        """The Goal gets a chance to decide what to do.

        It returns a list of actions to perform, plus gets a chance
        to change the goal stack, possibly causing another goal to be enqueued, or 
        for itself to be de-queued.
        """
        return []

    def goal_completed(self, goals: list):
        """Remove ourselves from the stack of goals.
        """
        goals.pop()
