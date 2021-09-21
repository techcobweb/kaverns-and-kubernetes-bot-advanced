
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
from .seek_point_goal import SeekPointGoal


class AttackEntity(SeekPointGoal):
    """
    A goal which homes in on a particular entity, attacking it.
    """

    def __init__(self, target_entity_id=None, target_entity_name=None):
        super().__init__()
        self._target_entity_id = target_entity_id
        self._target_entity_name = target_entity_name

    def __str__(self):
        return "AttackEntity {} {}".format(self._target_entity_name, self._target_entity_id)

    def acquire_target(self, me: Entity, state: State) -> bool:
        possible_enemies = state.entities.get_all()

        self._logger.debug("Acquiring enemy target if we can...")
        self._logger.debug("me: %s %s", me.identifier, me)

        # Big scores are entities we want to go after...
        best_enemy_score = 0
        best_enemy = None
        for enemy in possible_enemies:

            if enemy.identifier != me.identifier:

                enemy_score = self.score_enemy(enemy=enemy, me=me, state=state)
                if enemy_score > best_enemy_score:
                    self._logger.debug("Thats the best so far...")
                    best_enemy_score = enemy_score
                    best_enemy = enemy

        # Only bother with targets with big enough scores.
        if best_enemy_score > 0:
            self._target_entity_id = best_enemy.identifier
            self._target_entity_name = best_enemy.name

        if self._target_entity_id is None:
            return False

        return True

    def score_enemy(self, enemy: Entity, me: Entity, state: State) -> int:
        enemy_score = 0

        # Go for the local enemies first...
        path_to_enemy = self._path_finder.find_path(from_point=me.position,
                                                    to_point=enemy.position,
                                                    state=state)
        if path_to_enemy is None:
            # Can't find a way to this enemy, so ignore it.
            enemy_score -= 5000
        else:
            enemy_score += 500 - len(path_to_enemy)

        # Look at the enemy name. If it is one of our bots, try
        # not to target it unless it's the only option around.

        # The names of the bot entities have a '-nnnn' attached.
        # Where 'nnnn' is a random number.
        my_name_parts = me.name.split('-')
        # The last part of the name is my random number.
        number_part = my_name_parts[-1]
        if number_part.isnumeric():

            my_bot_number = int(number_part)

            # The first part is our name prefix. Normally "assassin"
            my_prefix = my_name_parts[0]

            if enemy.name.startswith(my_prefix):
                # It's another instance of our bot.
                enemy_score -= 100

                enemy_name_parts = enemy.name.split('-')
                enemy_bot_number_part = enemy_name_parts[-1]
                if enemy_bot_number_part.isnumeric():
                    enemy_bot_number = int()

                    if my_bot_number > enemy_bot_number:
                        # Don't target assassin bots with a higher number than me.
                        enemy_score -= 20

        self._logger.debug("Entity %s at %s has a score of %s id:%s",
                           enemy.name, enemy.position, enemy_score, enemy.identifier)
        return enemy_score

    @property
    def target_entity_id(self) -> Entity:
        return self._target_entity_id

    def decide_actions(self, me: Entity, state: State, goals) -> [Action]:
        """ move towards our target entity """
        actions = []

        if self._target_entity_id is None:
            self._logger.debug(
                "Not yet locked onto a target.")
            locked_on = self.acquire_target(me, state)
            if not locked_on:
                self._logger.debug("can't lock onto a target")
                goals.pop()

        if self._target_entity_id is not None:
            self.move_towards_enemy(state, me, actions, goals)

        return actions

    def move_towards_enemy(self, state: State, me: Entity, actions: [Action], goals: [Goal]):
        # We have a target entity to attack

        target_entity = state.entities.get_by_id(
            self._target_entity_id)

        if target_entity is None:
            self._logger.debug(
                "Enemy we were targetting to attack is not there now")

            self._logger.debug(str(state.entities))

            # Forget our goal. It is achieved.
            goals.pop()

        else:
            # target entity still exists.

            # Use a path-finder to find a route to it.
            path = self._path_finder.find_path(from_point=me.position,
                                               to_point=target_entity.position,
                                               state=state)

            if path is None:
                # Can't find a path to that entity.
                self._logger.debug(
                    "Can't plot a route to the target. Ending goal.")
                goals.pop()

            else:
                self._logger.debug(self._path_printer.render_path(
                    state, path, me.position.z, me.position))

                # There is a path to follow
                path.pop(0)  # Ignore our current location/first item.

                # The first hop to our destination is...

                if len(path) > 0:
                    self.move_along_path(state, path, me, actions)
                else:
                    self._logger.debug(
                        "Plot to target is zero length. Maybe the enemy died ?")
                    goals.pop()
