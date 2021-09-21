"""
A brain is something which does the thinking, and decides what the bot is
going to do.
"""

import random
import logging
from enum import Enum
from ..navigation.point import Point
from .item_handling_brain import ItemHandlingBrain
from ..state.entity import Entity
from ..state.state import State
from ..goals.goal import Goal
from ..state.item import Item
from ..goals.choose_goal import ChooseGoalGoal
from ..goals.seek_item_goal import SeekItemGoal
from ..goals.attack_goal import AttackEntity


# Only has any effect when running tests.
# logging.basicConfig(level=logging.DEBUG)


class MegaBrain(ItemHandlingBrain):
    """
    A smarter brain than the basic one we get students to start with.
    """

    def __init__(self):
        super().__init__()

        # Keep a track of how many items are visible to us.
        # If more become visible than before, then we can decide
        # what to do again, possibly interrupting our current goal
        # by adding another goal to our goal stack.
        self._items_visible_count = 0

    def decide_pre_move_actions(self, me, state, actions):
        # self._logger.debug("Megabrain: decide_pre_move_actions")
        super().decide_pre_move_actions(me, state, actions)
        self._monitor_new_items_available(state)
        self._detect_local_enemies(me, state)

    def create_goal(self):
        self._goals.append(ChooseGoalGoal())

    def _monitor_new_items_available(self, state: State):
        """
        Monitor for changes to the number of items we know about.

        We only care about useful items. Ignore any others.
        """
        all_items = state.items.get_as_list()
        useful_item_count = 0

        for item in all_items:
            if item.edible or item.wearable or item.wieldable:
                useful_item_count += 1

        if useful_item_count != self._items_visible_count:
            self._goals.append(ChooseGoalGoal())
            self._goals.append(SeekItemGoal())
        self._items_visible_count = useful_item_count

    def _detect_local_enemies(self, me: Entity, state: State) -> None:
        """
        If we are very near other entities, they may/will probably be
        trying to attack us.

        So put outselves in fight mode... and hit them back.
        """

        me = state.find_my_entity()

        # No point finding enemies if we have no weapon.
        if me.current_weapon is not None:

            my_position = me.position

            frontier_points = [my_position]
            closed_points = []

            found_enemies = False
            search_distance = 3
            while search_distance > 0 and not found_enemies:
                # Expand frontiers
                new_frontier_points = []
                for frontier_point in frontier_points:
                    neighbours = state.dungeon_map.get_neighbour_points(
                        frontier_point)

                    for neighbour in neighbours:
                        if (neighbour not in closed_points) and (neighbour not in frontier_points):
                            new_frontier_points.append(neighbour)

                    closed_points.append(frontier_point)

                frontier_points = new_frontier_points

                for frontier_point in frontier_points:
                    enemies_near_me = state.entities.get_by_position(
                        frontier_point)

                    # Don't treat our brother-bots as enemies near me.
                    non_assassin_enemies_near_me = list()
                    my_prefix = me.name.split('-')[0]
                    for enemy in enemies_near_me:
                        if not enemy.name.startswith(my_prefix):
                            non_assassin_enemies_near_me.append(enemy)

                    # Are there any enemies left we want to attack ?
                    if len(non_assassin_enemies_near_me) > 0:
                        # There are enemies nearbye.
                        found_enemies = True

                search_distance -= 1

            if found_enemies:
                self._logger.debug("Enemy is near. Fight mode...")
                self._goals.append(AttackEntity())
