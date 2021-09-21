import logging
import numpy
from ..navigation.point import Point
from .cell import Cell
from ..navigation.direction import Direction


class DungeonMap:
    """
    Represents the entire map of the dungeon.
    Including all of the levels

    Also can tell you about possible neighnouring points you
    could move to from a specified point.

    """

    # A cell we can return if anyone asks what lies at coordinates

    def __init__(self, height=10, width=10, depth=1, entrance=Point(5, 5, 0), cells=None):
        """ Construct a dungeon which is solid walls of set dimensions. 
        cells which are not walls can later be set with the set_cell(...) method.
        """
        self._width = width
        self._height = height
        self._depth = depth
        self._entrance = entrance
        self._logger = logging.getLogger(__name__)
        self._neighbours = None
        self._gateway_points = None

        if cells is None:
            self._cells = numpy.empty((depth, height, width), dtype=object)
            for z in range(0, depth):
                for y in range(0, height):
                    for x in range(0, width):
                        self._cells[z, y, x] = Cell.create_wall_cell()
        else:
            self._cells = cells
        self._do_map_calculations()

    def _do_map_calculations(self):
        self._calculate_all_neighbours()
        self._gateway_points = self._calculate_gateway_points()

    @classmethod
    def from_wire_format(cls, map_raw_data):
        """ Construct a dungeon map using the network serialisation format. """

        # Parse the JSON into a structure of lists and dictionaries.
        map_data = map_raw_data
        # print(self.map_data)

        width = map_raw_data['width']
        height = map_raw_data['height']
        depth = map_raw_data['depth']
        entrance = Point.from_dictionary(map_raw_data['entrance'])

        # print('width:{width} height:{height} depth:{depth}'
        #         .format( width=self._width
        #                , height= self._height
        #                , depth=self._depth
        #                )
        #      )

        # In one go, read the map data into a numpy 3-D array of tuples.
        cells = numpy.asarray(map_data['tiles'])

        # Convert the 3-D array of tuples into a 3-D array of cell objects.
        # print("height:{} width:{} depth:{}".format(height, width, depth))
        for z in range(0, depth):
            for y in range(0, height):
                for x in range(0, width):
                    raw_cell_data = cells[z, y, x]
                    cell = Cell.from_wire_format(raw_cell_data)
                    cells[z, y, x] = cell

        entrance_data = map_data['entrance']
        entrance = Point(
            entrance_data['x'], entrance_data['y'], entrance_data['z'])

        dungeon = DungeonMap(height=height, width=width,
                             depth=depth, entrance=entrance, cells=cells)
        return dungeon

    @ property
    def height(self):
        return self._height

    @ property
    def width(self):
        return self._width

    @ property
    def depth(self):
        return self._depth

    def is_point_within_dungeon_dimenisons(self, point: Point) -> bool:
        """
        Checks whether the point is within the dimensions of the dungeon or not.

        Returns:
            true : It is within the dungeon limits.
            false : it isn't within the dungeon limits.
        """
        z = point.z
        y = point.y
        x = point.x
        is_within_dungeon = False
        if z >= 0 and y >= 0 and x >= 0 and z < self._depth and y < self._height and x < self._width:
            is_within_dungeon = True
        return is_within_dungeon

    def get_cell(self, point):
        if self.is_point_within_dungeon_dimenisons(point):

            result = self._cells[point.z, point.y, point.x]
        else:
            self._logger.warning(
                "%s,%s,%s Outside the dungeon of dimensions %s,%s,%s",
                point.x, point.y, point.z, self._width, self._height, self._depth)
            result = Cell.create_wall_cell()
        return result

    def set_cell(self, point, cell):

        if self.is_point_within_dungeon_dimenisons(point):
            self._cells[point.z, point.y, point.x] = cell
            self._do_map_calculations()
        else:
            self._logger.warning("%s %s %s Outside the dungeon of dimensions %s %s %s",
                                 point.x, point.y, point.z, self._width, self._height, self._depth)

    @property
    def entrance(self):
        return self._entrance

    @entrance.setter
    def entrance(self, entrance):
        self._entrance = entrance

    def is_walkable(self, point: Point) -> bool:
        """ Finds out if someone can walk in the specified cell point.
        If the point is outside of the dungeon, we assume they can't walk there.
        """
        is_walkable = False
        if self.is_point_within_dungeon_dimenisons(point):
            cell: Cell = self._cells[point.z, point.y, point.x]
            is_walkable = cell.is_walkable()
        return is_walkable

    def _calculate_all_neighbours(self):
        dungeon = self
        self._neighbours = {}
        for z in range(dungeon.depth):
            for y in range(dungeon.height):
                for x in range(dungeon.width):
                    point = Point(x, y, z)
                    self._calculate_point_neighbours(point)

    def _calculate_point_neighbours(self, point):
        neighbours = self._find_immediate_neighbours_of(point)
        self._neighbours[point] = neighbours

    def get_neighbour_points(self, point: Point) -> [Point]:
        """ Given a point , return a list of the immediate neighbouring points """
        return self._neighbours.get(point, [])

    def _find_immediate_neighbours_of(self,
                                      my_position: Point) -> [Point]:
        dungeon_map = self
        possible_points = []
        for point in my_position.neighbours_same_level:
            if dungeon_map.is_walkable(point):
                # print("Point {} is walkable".format(point))
                possible_points.append(point)

        my_cell = dungeon_map.get_cell(my_position)

        if my_cell.char == '<':
            # Up-stairs
            point_if_went_upstairs = my_position.get_neighbour(Direction.UP)
            possible_points.append(point_if_went_upstairs)
        elif my_cell.char == '>':
            # Down-stairs
            point_if_went_downstairs = my_position.get_neighbour(
                Direction.DOWN)
            possible_points.append(point_if_went_downstairs)

        if dungeon_map.entrance in possible_points:
            possible_points.remove(dungeon_map.entrance)

        return possible_points

    def get_stair_points(self, z_dungeon_level: int, direction: Direction) -> [Point]:
        """ Looks for all the stairs of a certain type on the specified dungeon level.

        z_dungeon_level - The z of the dunegon level to look at.
        direction - Either UP or DOWN stairs we can search for.

        """
        stair_points = []

        if (z_dungeon_level < 0) or (z_dungeon_level > self._depth):
            # There are no stairs on levels outside the dungeon.
            pass
        elif not direction in (Direction.UP, Direction.DOWN):
            # Only up and down are expected.
            pass
        else:
            # All the input parameters are good.
            desired_stair_glyph = '>'
            if direction == Direction.UP:
                desired_stair_glyph = '<'

            z = z_dungeon_level
            for x in range(self._width):
                for y in range(self.height):
                    cell = self._cells[z, y, x]
                    if cell.char == desired_stair_glyph:
                        stair_points.append(Point(x, y, z))

        return stair_points

    @property
    def gateway_points(self) -> [Point]:
        return self._gateway_points

    def _calculate_gateway_points(self) -> [Point]:
        gateway_points = []
        for z in range(self._depth):
            for x in range(self._width):
                for y in range(self.height):
                    cell = self._cells[z, y, x]
                    if cell.is_gateway:
                        p = Point(x, y, z)
                        self._logger.debug("Cell %s is a gateway cell.", p)
                        gateway_points.append(p)
        return gateway_points
