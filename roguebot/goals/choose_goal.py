import logging
from enum import Enum
from ..navigation.point import Point
from ..brains.ibrain import IBrain
from ..brains.item_handling_brain import ItemHandlingBrain
from ..navigation.path_printer import PathPrinter
from ..state.entity import Entity
from ..state.state import State
from ..action import Action, TakeAction, MoveAction, EatAction, WearAction, WieldAction
from ..navigation.path import PathFinder
from ..navigation.direction import Direction
from ..goals.goal import Goal
from ..state.item import Item
from .advanced_goal import AdvancedGoal
from .seek_item_goal import SeekItemGoal
from .seek_gateway_goal import SeekGatewayGoal
from .attack_goal import AttackEntity
from .seek_point_goal import SeekPointGoal


class ChooseGoalGoal(AdvancedGoal):
    """
    There are no other goals.
    So think what we want to do next.

    """

    def __str__(self):
        return "ChooseGoalGoal"

    def decide_actions(self, me: Entity, state: State, goals) -> [Action]:
        """
        Decide what to do next
        """
        # Remove outself from the goal stack, as we will make a decision
        # on what to do next.
        goals.pop()

        seek_item_goal = SeekItemGoal()
        got_target_item = seek_item_goal.acquire_target(me, state)
        if got_target_item:

            # There are items we know about
            # So we want get the items as a default.
            goals.append(seek_item_goal)
            self._logger.debug(
                "There is an item we want. Lets go get it. %s", seek_item_goal)

        else:

            # There are no items we know about.

            # There maybe someone we can attack ?
            # Don't bother if we are not packing a weapon.
            is_attack_planned = False
            if me.current_weapon is not None:

                attack_goal = AttackEntity()
                is_target_acquired = attack_goal.acquire_target(me, state)
                if is_target_acquired:
                    goals.append(attack_goal)
                    self._logger.debug("planned an attack")
                    is_attack_planned = True

            if not is_attack_planned:

                # So can we descend another level of dungeon to
                # find some ?
                if me.position.z + 1 >= state.dungeon_map.depth:
                    # We are already at the bottom of the dungeon.
                    # So target a gateway ?
                    self._logger.debug(
                        "No lower levels to search for items, aiming for the gateway now.")
                    new_goal = SeekGatewayGoal(state)
                    goals.append(new_goal)

                else:
                    # Find the stairs going up to this level, from the next
                    # level down.
                    # When we move down the stairs, any items on the lower
                    # level will be revealed to us.
                    stair_point = self.select_stairs(state, me.position.z+1)
                    if stair_point is None:
                        # There are no stairs to seek out.
                        # So go back to the entrance.
                        self._logger.debug(
                            "No stairs found, aiming for the entrance now.")
                        new_goal = SeekGatewayGoal(state)
                        goals.append(new_goal)

                    else:
                        # There is a stair on a lower level of the dungeon
                        # to go to. Hopefully there will be more items...
                        new_goal = SeekPointGoal(stair_point)
                        goals.append(new_goal)
                        self._logger.debug(
                            "Seeking stair point %s", stair_point)

        return []
