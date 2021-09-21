import logging
from enum import Enum
from ..navigation.point import Point
from ..brains.ibrain import IBrain
from ..brains.item_handling_brain import ItemHandlingBrain
from ..state.entity import Entity
from ..state.state import State
from ..action import Action, TakeAction, MoveAction, EatAction, WearAction, WieldAction
from ..navigation.path import PathFinder
from ..navigation.direction import Direction
from ..goals.goal import Goal
from ..state.item import Item
from ..goals.advanced_goal import AdvancedGoal
from ..navigation.path_printer import PathPrinter


MAX_MOVES_TO_BURST_SEND_AT_ONCE = 1


class SeekPointGoal(AdvancedGoal):
    """ A goal which homes in on a particular point...
    """

    def __init__(self, point=None):
        super().__init__()
        # Allows us to find routes to points.
        self._path_finder = PathFinder()
        self._path_printer = PathPrinter()

        # The point we are trying to reach with this goal.
        self._target_point = point

    def __str__(self):
        return "SeekPointGoal point:" + str(self._target_point)

    @property
    def target_point(self) -> Point:
        return self._target_point

    @target_point.setter
    def target_point(self, new_point: Point):
        self._target_point = new_point

    def decide_actions(self, me: Entity, state: State, goals) -> [Action]:
        """ move towards our target point """
        actions = super().decide_actions(me, state, goals)
        self.move_towards_point(state, me, actions, goals)
        return actions

    def move_towards_point(self, state: State, me: Entity, actions: [Action], goals):

        if self._target_point is not None:
            # We have a target location.
            # There is still an item there.
            # Use a path-finder to find a route to it.
            path = self._path_finder.find_path(from_point=me.position,
                                               to_point=self._target_point,
                                               state=state)

            if path is None:
                # Can't find a path to that point.
                # Forget it and choose another.
                self.no_path_available(me, state, goals)

            else:

                self._logger.debug(self._path_printer.render_path(
                    state, path, me.position.z, me.position))

                # There is a path to follow
                path.pop(0)  # Ignore our current location.

                # The first hop to our destination is...

                if len(path) > 0:
                    self.move_along_path(state, path, me, actions)

                else:
                    # We reached our destination
                    # Select another one.
                    self.destination_reached(goals)

    def move_along_path(self, state: State, path: [Point], me: Entity, actions: [Action]):
        """
        Enqueue a number of 'move' commands on the action list from our chosen path.
        """
        from_point = me.position

        moves_to_enqueue = MAX_MOVES_TO_BURST_SEND_AT_ONCE

        while moves_to_enqueue > 0 and len(path) > 0:
            moves_to_enqueue -= 1

            next_step_point = path.pop(0)
            # "Aiming move at {} from {}".format(next_step_point, me.position))

            direction = from_point.direction_of(
                next_step_point)

            move_action = MoveAction(direction)
            actions.append(move_action)

            from_point = next_step_point

    def destination_reached(self, goals):
        self._logger.debug(
            "Destination reached. %s", self._target_point)

        # Remove ourselves.
        goals.pop()

    def no_path_available(self, me, state, goals):
        self._logger.debug("No path to destination point.")

        # We can't get to the desired point. So forget this goal.
        goals.pop()
