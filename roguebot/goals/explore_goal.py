
import random
import logging
from ..brains.ibrain import IBrain
from ..navigation.point import Point
from ..navigation.path_printer import PathPrinter
from ..navigation.direction import Direction
from ..state.entity import Entity, Entities
from ..state.state import State
from ..action import Action, MoveAction
from .goal import Goal


TARGET_EXPLORE_TURN_COUNT = 100


class ExploreGoal(Goal):
    """A goal of exploring the dungeon at random for a bit.

    It wanders around for 100 moves, preferring to move to points it hasn't
    been to. After that it gives up and completes.

    """

    def __init__(self):
        """A goal of exploring the map a bit.

        Attributes:
            _turn_count (int): The number of turns this goal has had deciding what to do so far.
                Starts at 0, goes up to TARGET_EXPLORE_TURN_COUNT
            _places_visited (dict): The key is a Point, the value us the number of times that point
                has been visited so far.

        """
        super().__init__()
        self._turn_count = 0

        # A dict of places we have visited.
        # The key is the point, the value is the number of times we've been there.
        # So we can try going somewhere newer if there is a choice.
        self._places_visited = {}

    def decide_actions(self, me: Entity, state: State, goals: [Goal]) -> [Action]:
        """Move at random, preferrably away from where we have been before.

        Parameters:
            me (Entity): The Entity representing this bot
            state (State): The state of the world as we know it.
            goals (Goal): A stack of goals. Appending one to this list effectively causes
                that action to be schediled.
                The goal completes, and de-queues itself from the goal stack after 100 'turns'

        Returns:
            [Action] : An array of Action objects to be played out by the bot.
        """
        actions = super().decide_actions(me, state, goals)

        # For debugging, output the map with our bot position marked.
        self._logger.debug(self._path_printer.render_path(
            state=state,
            only_show_floor=me.position.z,
            me_point=me.position))

        self._logger.debug("hp:%s ac:%s weapon:%s armour:%s", me.hit_points,
                           me.armour_class, me.current_weapon, me.current_armour)

        # We have obviously visited this point, as we are here now...
        self._remember_we_visited_this_point(me.position)

        # List the places we could move to immediately...
        possible_points = state.dungeon_map.get_neighbour_points(me.position)

        # Remove any points where there are entities blocking the way.
        # As we don't want to bump into them.
        possible_points = self._remove_points_entities_are_standing_on(
            state.entities, possible_points)

        # Filter out points we've visited a lot already.
        best_points = self._find_best_scoring_points(possible_points)

        # We have a list of the best points.
        # choose one at random...
        # print("Choosing a point out of {}".format(best_points))
        chosen_point = self._choose_point(best_points, me.position)

        # Turn the point into a direction.
        chosen_direction = me.position.direction_of(chosen_point)

        # print("Chosen direction:{}".format(chosen_direction))
        if chosen_direction is not None:
            actions.append(MoveAction(chosen_direction))

        # If we've been exploring enough, consider this goal
        # complete.
        if self._turn_count > TARGET_EXPLORE_TURN_COUNT:
            self.goal_completed(goals)
        self._turn_count += 1

        return actions

    def _choose_point(self, best_points: list, my_position: Point) -> Point:
        """Given a list of points which are possible to move to, choose one.

        Parameters:
            best_points ([Point]): Points which we can consider.
            my_position (Point): Where I am. This can't be chosen.

        Returns:
            Point: The chosen point, picked out at random from the best_points
        """
        if len(best_points) == 0:
            # Nowhere to move to.
            chosen_point = my_position
        elif len(best_points) == 1:
            # Only one option. Best go there.
            chosen_point = best_points.pop()
        else:
            # More than one option. Choose randomly.
            chosen_point = random.choice(best_points)
        return chosen_point

    def _find_best_scoring_points(self, possible_points):
        """Score each point we could move to based on whether we've visited it before.
        """
        # Remember the highest scored points
        best_points = []
        best_score = 0
        for point in possible_points:

            # Get the number of times we've visited this point before, or
            # 0 if we've not visited it before.
            count_visited_before = self._places_visited.get(point, 0)

            score = 1000 - count_visited_before

            # print("score for point {} is {}. visited_before_count:{}".format(
            #     point, score, count_visited_before))
            if score > best_score:
                # Exceeded our best score so far. Start a new list of best points.
                best_points = [point]
                best_score = score

            elif score == best_score:
                # Matched the best score, so we have a choice of best points.
                best_points.append(point)

        return best_points

    def _remove_points_entities_are_standing_on(self, entities: Entities, possible_points: [Point]) -> None:
        """Remove any points from the possible points which have entities standing on them.
        So we don't bump into other entities.

        Parameters:
            entities (Entities): The entities we are trying to avoid.
            possible_points ([Point]): The points which are possible places we want to move to.


        """
        points_no_entities = []
        for point in possible_points:
            entities_at_point = entities.get_by_position(point)
            entity_count = len(entities_at_point)
            if entity_count == 0:
                points_no_entities.append(point)
        return points_no_entities

    def _remember_we_visited_this_point(self, point: Point) -> None:
        """Make a note that we just visited this point.

        Makes it slightly less likely that we'll want to visit the point in the future.

        Parameters:
            point (Point): The point we have just visited. 
            Bump the counter of this point up by one.

        """
        visited_count = self._places_visited.get(point, 0)
        visited_count += 1
        self._places_visited[point] = visited_count
