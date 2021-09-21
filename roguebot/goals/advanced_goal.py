
import random
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

# Only has any effect when running tests.
# logging.basicConfig(level=logging.DEBUG)


class AdvancedGoal(Goal):
    def __init__(self):
        super().__init__()

        # Allows us to find routes to points.
        self._path_finder = PathFinder()

    def select_stairs(self, state: State, z_dungeon_level: int):
        stairs_list = state.dungeon_map.get_stair_points(
            z_dungeon_level, Direction.UP)

        if len(stairs_list) == 0:
            # No stairs
            selected_stairs = None
        else:
            selected_stairs = random.choice(stairs_list)

        return selected_stairs
