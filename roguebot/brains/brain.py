"""
A brain is something which does the thinking, and decides what the bot is
going to do.
"""

import random
import logging
from ..navigation.point import Point
from .ibrain import IBrain
from ..state.entity import Entity
from ..state.state import State
from ..action import Action
from ..goals.goal import Goal
from ..goals.explore_goal import ExploreGoal

# logging.basicConfig(level=logging.DEBUG)


class GoalDrivenBrain(IBrain):

    """A brain which sets goals and then tried to achieve them.
    """

    def __init__(self):
        """Maintain a stack of goals.

        The one at the end of the list is the one to do next.
        """
        super().__init__()
        self._goals = []
        self._logger = logging.getLogger(__name__)

    def clear(self):
        """
        Clear the brain of any state it may have accrued.
        We have probably just entered a new dungeon, so 
        any goals or suchlike are now not relevent.
        """
        self._goals = []
        self._logger.debug("Cleared the brain of all previous thoughts.")

    def decide_actions(self, state: State) -> [Action]:
        """Decides what actions we want to do next.

        Parameters:
            state (State): The state of the world as we know it.

        Returns:
            [Action] : An array of actions we want the bot's body
            to perform next. The list can be empty, implying 
            that it should do nothing.
        """
        # self._logger.debug("> decide_actions")

        # We want to return a list of actions.
        actions = []

        me = state.find_my_entity()

        # self._logger.debug("state: {}".format(state))
        # self._logger.debug("me:{}".format(me))

        self.decide_pre_move_actions(me, state, actions)

        # Ensure there will never be an empty goals list.
        if len(self._goals) == 0:
            self.create_goal()

        # [-1] index gives the last entry in the list.
        if len(self._goals) > 0:
            goal_to_run = self._goals[-1]

            # A status line. Summarising our state.
            weapon = me.current_weapon
            weapon_name = 'None'
            if weapon is not None:
                weapon_name = weapon.name
            self._logger.debug("me: %s at %s", me.name, me.position)
            self._logger.debug("hp:%s ac:%s weapon:%s",
                               me.hit_points, me.armour_class, weapon_name)

            self._logger.debug("decide_actions using goal:%s", goal_to_run)

            self._logger.debug("Goal stack:")
            for goal in self._goals:
                self._logger.debug("  %s", goal)

            # record our current status in case anyone is interrested.
            self._status_summary = {
                "hp": me.hit_points,
                "ac": me.armour_class,
                "weapon": me.current_weapon,
                "armour": me.current_armour,
                "name": me.name,
                "point": me.position.to_dictionary(),
                "goal": str(goal_to_run)
            }

            self._logger.debug("goal:%s", goal_to_run)

            actions_from_goal = goal_to_run.decide_actions(
                me, state, self._goals)

            if actions_from_goal is not None:
                for action in actions_from_goal:
                    actions.append(action)

        return actions

    def decide_pre_move_actions(self, me: Entity, state: State, actions: [Action]) -> None:
        """ 
        Gives subclasses of this class a chance to do 
        things before we try to move.

        Parameters:
            me (Entity): Entity representing the bot
            state (State): The state of the world as we know it.
            actions ([Action]): An array of Action objects. 
                The array can be appended to if we want to generate new actions.

        Note:
            You might like to add behaviours such as taking items, eating items, 
            wearing or wielding items here.
        """

    def create_goal(self):
        """We create an explore goal. 

        Which explores around for a bit.

        """
        self._goals.append(ExploreGoal())
