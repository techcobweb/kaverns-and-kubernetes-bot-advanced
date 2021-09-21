"""
A small patch of land within a dungeon.
"""

from ..navigation.point import Point


class Cell:
    """
    A single square small patch of land in the dungeon map.
    """

    def __init__(self, char: str, is_walkable: bool = False, is_gateway: bool = False):
        """ Construct a cell explicitly with the attributes we care about """
        self._char: str = char
        self._is_walkable: bool = is_walkable
        self._position: Point = None
        self._is_gateway = is_gateway

    @classmethod
    def from_wire_format(cls, cell_data):
        """ Given a cell in the dungeon map wire format, construct the cell object """
        char: str = cell_data['char']
        is_walkable: bool = cell_data['walkable']
        is_gateway = False
        if 'gateway' in cell_data.get('description', ''):
            is_gateway = True
        return Cell(char, is_walkable, is_gateway)

    @classmethod
    def create_wall_cell(cls):
        return Cell(char="#", is_walkable=False, is_gateway=False)

    @classmethod
    def create_gateway_cell(cls):
        return Cell(char='*', is_walkable=True, is_gateway=True)

    @classmethod
    def create_empty_cell(cls):
        return Cell(char=" ", is_walkable=True, is_gateway=False)

    @classmethod
    def create_stairs_cell(cls, char):
        return Cell(char=char, is_walkable=True, is_gateway=False)

    def __str__(self):
        return self._char

    @property
    def char(self):
        return self._char

    def is_walkable(self):
        return self._is_walkable

    @property
    def position(self) -> Point:
        return self._position

    @position.setter
    def position(self, new_position: Point):
        self._position = new_position

    @property
    def is_gateway(self) -> bool:
        return self._is_gateway
