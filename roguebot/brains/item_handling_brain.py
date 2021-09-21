import logging
from queue import PriorityQueue
from ..navigation.point import Point
from .ibrain import IBrain
from .brain import GoalDrivenBrain
from ..state.entity import Entity
from ..state.state import State
from ..action import Action, TakeAction, EatAction, WieldAction, WearAction
from ..goals.goal import Goal
from ..goals.explore_goal import ExploreGoal
from ..state.item import Item


class ItemHandlingBrain(GoalDrivenBrain):

    """
    A bot which picks up and uses items it finds.
    """

    def decide_pre_move_actions(self, me: Entity, state: State, actions: [Action]):
        # self._logger.debug("ItemHandlingBrain: decide_pre_move_actions")
        self.decide_take_action(state, me, actions)
        self.decide_eat_action(me, actions)
        self.decide_wear_action(me, actions)
        self.decide_wield_action(me, actions)

    def decide_eat_action(self, me, actions):
        """ If we have something edible in the inventory, eat ! Yum ! """
        for item in me.inventory:
            # self._logger.debug(
            #     "  decide_eat_action : Looking to see if Item %s is edible", item.name)
            if item.edible and me.hunger > 0:
                self._logger.info(
                    " decide_eat_action : Item %s is edible. yummy ! ", item.name)
                action = EatAction(item.name)
                actions.append(action)

    def decide_wear_action(self, me, actions):
        """ If we are not wearing anything, and we have something in the
        inventory which can be worn, then wear that item
        """
        best_armour = None
        best_armour_class = 10
        for item in me.inventory:
            if item.wearable:
                if item.armour_class < best_armour_class:
                    best_armour = item
                    best_armour_class = item.armour_class

        current_armour_class = 10
        if me.current_armour is not None:
            current_armour_class = me.current_armour.armour_class

        if best_armour is not None:
            if current_armour_class > best_armour_class:
                action = WearAction(best_armour.name)
                actions.append(action)

    def decide_wield_action(self, me, actions):
        """ If we don't already have a weapon drawn, but one is in
        the inventory, then wield it.
        """

        # Lets find the most deadly weapon.
        best_weapon = None
        best_weapon_damage = 0
        for item in me.inventory:
            if item.wieldable:
                if item.damage > best_weapon_damage:
                    best_weapon = item
                    best_weapon_damage = item.damage

        if best_weapon is not None:
            # We have at least one weapon to wield...
            if me.current_weapon is None:
                # Currently not holding a weapon
                self._logger.info(
                    "Our best weapon is '%s', so wielding it.", best_weapon.name)
                action = WieldAction(best_weapon.name)
                actions.append(action)
            else:
                # Holding a weapon already
                if best_weapon.damage > me.current_weapon.damage:
                    self._logger.info("Our current weapon is '%s'(damage:%s), but '%s'(damage:%s) is better.",
                                      me.current_weapon.name, me.current_weapon.damage, best_weapon.name, best_weapon.damage)
                    action = WieldAction(None)
                    actions.append(action)
                    action = WieldAction(best_weapon.name)
                    actions.append(action)

    def decide_take_action(
            self,
            state: State,
            me: Entity,
            actions: [Action]):
        """If we are in the same place as an item, take it.

        But only if it's useful. Otherwise leave it.
        """
        items_at_my_location = state.items.get_items_at_position(me.position)
        if len(items_at_my_location) > 0:
            # There is something to pick up. If it's any good.

            for item in items_at_my_location:
                if self.is_item_useful(item):
                    action = TakeAction(item.name)
                    actions.append(action)

    def is_item_useful(self, item: Item) -> bool:
        is_useful = True
        if (not item.wearable) and (not item.edible) and (not item.wieldable):
            # Item is pretty useless. Ignore.
            is_useful = False
        return is_useful
