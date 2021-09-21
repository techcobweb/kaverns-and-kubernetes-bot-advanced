"""A collection of path-finding routines.
"""

from enum import Enum
import random
import logging
from queue import PriorityQueue
from .point import Point
from ..state.entity import Entity
from ..state.state import State


# logging.basicConfig(level=logging.DEBUG)

class PathFinder():
    """
    Something which finds paths between points.
    """

    DIFFERENT_LEVEL_DISTANCE_SCORE = 30
    """
    How much penulty on the move score do we apply if the source and 
    target point are on different levels of the dungeon ?

    ie: It's worth this many points of movement to go up/down one flight of stairs.

    Which should mean we prefer investigating most points on the same level, before we
    look at routes/points on levels up/down stairs.
    """

    MAX_THINKING_POINTS_CONSIDERED = 500000
    """
    The top limit on the number of points we examine before concluding that
    there is no feasable route to the destination.

    The same point may be examined multiple times if it can be 
    approached from different sides.
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(level=logging.INFO)
        self._attempt_limit = PathFinder.MAX_THINKING_POINTS_CONSIDERED

    @property
    def attempt_limit(self):
        return self._attempt_limit

    @attempt_limit.setter
    def attempt_limit(self, new_limit):
        self._attempt_limit = new_limit

    def score_point_distance(self, from_point: Point, to_point: Point) -> int:
        """score the distance between two points.

        Parameters:
            from_point (Point): Navigating from this point, to the to_point.
            to_point   (Point): The target point we are navigating to, and we want scored.

        Returns:
            score (int): A score.
                Low scores are good. 0 is no distance between points. exact same.
                Higher scores are bad. Points are far away.

                Being on a different level is bad, and increases the score by a lot.
                as its' very far away.
        """
        x_difference = abs(to_point.x - from_point.x)
        y_difference = abs(to_point.y - from_point.y)
        z_difference = abs(to_point.z - from_point.z)
        distance_score = x_difference + y_difference + \
            (z_difference * PathFinder.DIFFERENT_LEVEL_DISTANCE_SCORE)
        return distance_score

    def find_path(self, from_point: Point, to_point: Point, state: State) -> [Point]:
        """Finds one of the routes between two points.

        There may be more, but only one is returned.
        The first one we find.

        Parameters:
            from_point (Point): Where we are navigating from. If a route is found, this will
                be the first point in the returned route.
            to_point (Point): Where we are navigating to. If a route is found, this will
                be the last point in the returned route.
            state (State): The state of the world. This is needed to find our way around,
                so we can avoid walls and other entities blocking our path.

        Returns:
            ([Point]) : A list of points, starting with where we are, and ending
                at the target point, or None if we can't find a way between the two points.

        Note:
            This is the A* algorithm. It's a combination of Dijkstra’s Algorithm
            and the Greedy Best-First algorithm.

            It finds one of the shortest paths available between the points, but doesn't
            examine all possibilities due to the use of the score_point_distance
            heuristic algorithm.

        """

        frontier = PriorityQueue()
        frontier.put((0, from_point))

        came_from = {}
        cost_so_far = {}

        came_from[from_point] = None
        cost_so_far[from_point] = 0

        if state is not None:
            gateway_points = state.dungeon_map.gateway_points
        else:
            gateway_points = []

        if state is not None:
            gateway_points = state.dungeon_map.gateway_points
        else:
            gateway_points = []

        attempt_count = self._attempt_limit
        current = None
        while not frontier.empty() and attempt_count > 0:
            current = frontier.get()[1]

            if current == to_point:
                # We found our target point!
                break

            for next_neighbour in state.dungeon_map.get_neighbour_points(current):
                entities_at_this_spot = len(
                    state.entities.get_by_position(next_neighbour))
                if (next_neighbour == to_point) or (
                        (entities_at_this_spot == 0) and (next_neighbour not in gateway_points)):
                    # Limit the number of possibilities we can look at.
                    # To stop getting into exhaustive CPU loops.
                    attempt_count -= 1

                    # Points are penalised from being away from the from_point-point
                    # We are 1 cost away from each neighbour, as it's a grid.
                    new_cost = cost_so_far[current] + 1

                    if next_neighbour not in cost_so_far or new_cost < cost_so_far[next_neighbour]:
                        # Record the cost for this point, which may over-write
                        # the cost of this point if we visited it as a neighbour
                        # of another frontier point.
                        cost_so_far[next_neighbour] = new_cost

                        # The point gets more score for being closer to the
                        # target point also.
                        priority = new_cost + \
                            self.score_point_distance(next_neighbour, to_point)

                        frontier.put((priority, next_neighbour))

                        # Possibly over-write the came-from point if
                        # we have examined next point already, but this one
                        # has a better score.
                        # This means we don't follow walls around a room, but
                        # cross the room using the a central area.
                        came_from[next_neighbour] = current

        # Now extract the path from the chain of points left in the
        # came_from array
        path = None
        # Path returned only if we reached our goal point.
        if current == to_point:
            path = []

            path.append(current)
            done = False
            while not done:
                previous = came_from.get(current, None)
                if previous is None:
                    done = True
                else:
                    path.append(previous)
                    current = previous
            path.reverse()

        return path
