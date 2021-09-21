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
from ..goals.seek_point_goal import SeekPointGoal


class SeekItemGoal(SeekPointGoal):

    def __init__(self, point=None, target_item_name: str = None):
        super().__init__(point)
        self._target_item_name = target_item_name

    def __str__(self):
        return "SeekItemGoal point: {} target-item: {}".format(self._target_point, self._target_item_name)

    def acquire_target(self, me: Entity, state: State) -> bool:
        """Look at the state and create a seekItemGoal if there is anything
        we really want to go get.

        Parameters:
            me (Entity): Myself. So I can see what I have in my inventory if required.
                It may help rank which items are more important.
            state (State): The world state as we know it. Including all the items we
                already know about. There may be more on other levels, or dropped
                by other bots as they die, or some may re-spawn...etc.

        Returns:
            bool : False if there is nothing worth targeting.
                or true if we have an item to seek, with the target item all set
                and ready to go.
        """
        self._logger.debug("trying to acquire an item as a target...")

        all_known_items = state.items.get_as_list()

        selected_item = None
        selected_item_score = 0

        for item in all_known_items:
            utility_score = self.score_item(me, item, state)
            if utility_score > selected_item_score:
                self._logger.debug("Item is best so far.")
                selected_item = item
                selected_item_score = utility_score

        if selected_item_score <= 0 or selected_item is None:
            return False

        self._logger.debug(
            "Selected item target %s at %s", selected_item, selected_item.position)
        self._target_point = selected_item.position
        self._target_item_name = selected_item.name

        return True

    def score_item(self, me: Entity, item: Item, state: State) -> int:
        """Scores the item in terms of desireability.

        Returns:
            score (int): The desireablility of this item.
                Useless items have zero score.
                Valuable items have a higher score.
                Items far away have a smaller score.
        """
        item_score = 0

        if item.edible:
            item_score += 100

        if item.wearable:
            item_score += 100

        if item.wieldable:
            # Is it a great item ? compared to what we carry now ?
            current_damage = 0
            if me.current_weapon is not None:
                current_damage = me.current_weapon.damage

            item_damage = item.damage
            if item_damage > current_damage:
                item_score += 200
            else:
                # Still worth taking, just to stop others getting it.
                item_score += 50

        if item_score > 0:
            # This item is a contender.

            # Look at how easy it is to reach the item...
            from_point = me.position
            to_point = item.position

            self._logger.debug(
                "Examining %s ... in more detail...", item)

            path = self._path_finder.find_path(from_point, to_point, state)
            if path is None:
                self._logger.debug(
                    "Can't find a route to item %s ...", item)
                self._logger.debug("so forgetting it for now...")
                # Pretty much rule this item out for now.
                item_score -= 1000

            else:
                item_score += 200 - (len(path) * 2)
                self._logger.debug(
                    "Score for %s is %s ...", item, item_score)

        return item_score

    def decide_actions(self, me: Entity, state: State, goals) -> [Action]:

        actions = []

        if self._target_point is None:
            is_target_acquired = self.acquire_target(me, state)

            if not is_target_acquired:
                self.no_items_to_seek(goals)
            else:
                # Home in on where the item is.
                self._logger.info("Targetting item '%s' at %s",
                                  self._target_item_name, self._target_point)

        else:
            # We already have a target point

            if self.is_item_still_there(state):

                # Home in on it some more.
                actions = super().decide_actions(me, state, goals)

            else:
                self._logger.debug("Someone took the item we were after")
                # Remove this goal. It has been abandoned.
                goals.pop()

        return actions

    def is_item_still_there(self, state: State) -> bool:
        """ Make sure there is still an item there at the target point """
        is_still_there = True
        items_being_targetted = state.items.get_items_at_position(
            self._target_point)
        if len(items_being_targetted) == 0:
            # The items we were targetting have gone.
            # Select another target item next time around...
            is_still_there = False
        return is_still_there

    def no_items_to_seek(self, goals):
        self._logger.debug("No items left to seek.")
        # Pop ourselves off the goal list.
        goals.pop()

    def destination_reached(self, goals):
        super().destination_reached(goals)

        # line-up another goal.
        new_goal = SeekItemGoal()
        goals.append(new_goal)

    def no_path_available(self, me, state, goals):
        super().no_path_available(me, state, goals)

        # Choose a different item. If there is one.
        new_goal = SeekItemGoal()
        if new_goal.acquire_target(me, state):
            goals.append(new_goal)
