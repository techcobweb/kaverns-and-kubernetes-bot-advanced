"""The direction of travel.
"""

from enum import Enum


class Direction(Enum):
    """ A direction of travel

    The coordinate system origin is top-left.
    So (0,0,0) is top left on the hightest dungeon level.

    Going deeper into the dungeon (going down) increases the Z value.
    Going up reduces Z.

    Going east, increases X
    Going north, reduces Y
    """
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4
    UP = 5
    DOWN = 6
