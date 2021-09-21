"""An immutable Point in a 3-D space.
"""

from .direction import Direction


class Point:
    """An immutable point in the 3-D dungeon space.

    The coordinate system origin is top-left.
    So (0,0,0) is top left on the hightest dungeon level.

    Going deeper into the dungeon (going down) increases the Z value.
    Going up reduces Z.

    Going east, increases X
    Going north, reduces Y
    """

    def __init__(self, x: int, y: int, z: int):
        """Create a point with 3-D coordinates.

        Parameters:
            x (int): x
            y (int): y
            z (int): z
        """
        self._x = x
        self._y = y
        self._z = z

    def __str__(self) -> str:
        return "Point({},{},{})".format(self._x, self._y, self._z)

    def __repr__(self):
        """If there is a list of objects, and someone prints the list,
        it would normally output some object reference hex number.
        Using this method allows us to print out the string form of the
        points instead. Given points are singletons and immutable...
        """
        return str(self)

    def __hash__(self):
        """A mostly unique has of the content of this object

        Points with the same x,y,z values will have the same hashcode.
        """
        return self._x + 500 * self._y + 10000 * self._z

    def __lt__(self, other):
        """Is the other point less than this one ?

        What does this mean w.r.t. points in 3-D ?
        Lets assume it means that the hash-codes are less.

        These are made up from the x, y and z values themselves.
        See the __hash__() method.
        """
        return hash(self) < hash(other)

    @classmethod
    def from_dictionary(cls, data):
        """Create a Point obect from a dictionary.
        """
        return Point(data['x'], data['y'], data['z'])

    def to_dictionary(self) -> dict:
        return {"x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def from_point(cls, point_to_clone):
        """Clone the point.
        """
        return Point(point_to_clone.x, point_to_clone.y, point_to_clone.z)

    def __eq__(self, other) -> bool:
        """Is something equal to this point ?

        Only if that thing is itself a point, and the x, y, and z match.
        """
        is_same = False
        if self._x == other._x and self._y == other._y and self._z == other._z:
            is_same = True
        # else:
            # print(self._x ,other._x , self._y , other._y , self._z , other._z )
        return is_same

    @property
    def x(self) -> int:
        """Get the x coordinate in a 3-D space.
        """
        return self._x

    @property
    def y(self) -> int:
        """Get the y coordinate in a 3-D space.
        """
        return self._y

    @property
    def z(self) -> int:
        """Get the z coordinate in a 3-D space.
        """
        return self._z

    def get_neighbour(self, direction: Direction):
        """If I am at this point, and I move in a specified
        direction, which point would I end up at ?

        Parameters:
            direction (Direction): The direction I am intending to move in.

        Returns:
            Point : The point I would end up at if I went in that direction.

        """
        switcher = {
            Direction.NORTH:  Point(self._x, self._y-1, self._z),
            Direction.EAST:   Point(self._x+1, self._y, self._z),
            Direction.SOUTH:  Point(self._x, self._y+1, self._z),
            Direction.WEST:   Point(self._x-1, self._y, self._z),
            Direction.UP:     Point(self._x, self._y, self._z-1),
            Direction.DOWN:   Point(self._x, self._y, self._z+1),
        }
        return switcher.get(direction, None)

    @property
    def neighbours_same_level(self):
        """Gets a list of all the immediate neighbour points, which are
        on the same dungeon level.

        Returns:
            [Point] : A list of points which are neighbours of this Point.

        """
        neighbours = []
        for direction in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
            neighbours.append(self.get_neighbour(direction))
        return neighbours

    def direction_of(self, to_point) -> Direction:
        """Find the direction we need to take to get from 'this' point to the to_point.

        Parameters:
            to_point (Point): The direction we are heading to from the 'this' point.

        Returns:
            Direction : A direction, indicating which direction you would have to take
            to get from 'this' point to the to_point.

        Note: Only works if the 'this' point is directly next to the target point,
        else None is chosen.
        """
        dir_found = None
        for direction in Direction:
            if self.get_neighbour(direction) == to_point:
                dir_found = direction
                break
        return dir_found
