
import logging
import random
from enum import Enum
from ..navigation.point import Point
from ..brains.ibrain import IBrain
from ..brains.item_handling_brain import ItemHandlingBrain
from ..state.entity import Entity
from ..state.state import State
from ..action import Action, TakeAction, MoveAction, EatAction, WearAction, WieldAction
from ..navigation.path import PathFinder
from ..navigation.direction import Direction
from .goal import Goal
from ..state.item import Item
from .advanced_goal import AdvancedGoal
from .seek_point_goal import SeekPointGoal


class SeekGatewayGoal(SeekPointGoal):

    def __init__(self, state):
        super().__init__()
        self._chosen_gateway = None
        gateways = state.dungeon_map.gateway_points
        if gateways is None or len(gateways) == 0:
            self._logger.debug("No gateways known.")
            super().__init__(Point(99, 99, 99))
        else:
            self._chosen_gateway = random.choice(gateways)
            self._logger.debug("Chose gateway %s", self._chosen_gateway)
            self.target_point = self._chosen_gateway

        self.target_point = self._chosen_gateway

    def __str__(self):
        return "SeekGatewayGoal seeking {}".format(self._chosen_gateway)

    def no_path_available(self, me, state, goals):
        self._logger.debug("No path to gateway")
        if me.position.z <= 0:
            # We are already on the top level.
            self._logger("Already on top floor. Giving up.")

            # So really can't find the route.
            # Give up on the entrance. Try something else.
            goals.pop()

        else:
            # Ok. So lets take some stairs which lead up then.
            stair_point = self.select_stairs(state, me.position.z-1)
            if stair_point is None:
                # Odd. There should be stairs coming down to this level...
                # Give up on the entrance. Try something else.
                self._logger.debug("Can't find stairs going up!")
                goals.pop()
            else:
                # Queue-up the goal to walk to the stairs on the level above.
                # Once there, we revert to looking for the entrance.
                self._logger.debug("Target stairs going up at %s", stair_point)
                extra_goal = SeekPointGoal(stair_point)
                goals.append(extra_goal)
