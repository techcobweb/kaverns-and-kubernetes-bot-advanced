import functools
import types
from abc import ABC, abstractmethod, abstractproperty
from ..action import Action
from ..state.state import State


class IBrain(ABC):
    """
    A base class to a thinking brain

    Properties:
        max_actions_per_turn (int) : A number, minumum 1, default of 1.
        Indicates the maximum number of 'move' commands are to be sent to the server
        in one 'turn'.
    """

    def __init__(self):
        self._max_actions_per_turn = 1
        self._status_summary = {}

    def clear(self):
        """
        Clear the brain of any state it may have accrued.
        We have probably just entered a new dungeon, so 
        any goals or suchlike are now not relevent.
        """

    @abstractmethod
    def decide_actions(self, state: State) -> [Action]:
        """
        Given lots of facts, decide what actions need performing.
        """

    @property
    def max_actions_per_turn(self) -> int:
        return self._max_actions_per_turn

    @max_actions_per_turn.setter
    def max_actions_per_turn(self, max_actions_per_turn: int = 1):
        self._max_actions_per_turn = max_actions_per_turn

    @property
    def status_summary(self) -> dict:
        """
        A summary of the status, housed in a dict object.
        """
        return self._status_summary

    @status_summary.setter
    def status_summary(self, new_status: dict) -> None:
        self._status_summary = new_status
