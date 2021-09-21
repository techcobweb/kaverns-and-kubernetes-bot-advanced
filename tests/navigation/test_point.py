import unittest
from roguebot.navigation.point import Point
from roguebot.navigation.direction import Direction
from assertpy import assert_that


class TestPoint(unittest.TestCase):
    def test_as_dict(self):
        point = Point(1, 2, 3)
        assert_that(point.to_dictionary().get("x")).is_equal_to(1)
        assert_that(point.to_dictionary().get("y")).is_equal_to(2)
        assert_that(point.to_dictionary().get("z")).is_equal_to(3)

    def test_str_of_origin_is_rendered(self):
        point = Point(0, 0, 0)
        assert_that(str(point)).is_equal_to("Point(0,0,0)")

    def test_repr_of_origin_is_rendered(self):
        point = Point(0, 0, 0)
        assert_that(str([point])).is_equal_to("[Point(0,0,0)]")

    def test_stores_coordinates(self):
        point = Point(1, 2, 3)
        self.assertEqual(1, point.x)

    def test_from_point(self):
        point = Point(1, 2, 3)
        point2 = Point.from_point(point)
        self.assertEqual(point, point2)

    def test_two_objects_equal(self):
        point1 = Point(1, 2, 3)
        point2 = Point(1, 2, 3)
        self.assertEqual(point1, point2)

    def test_neighbour_north(self):
        point = Point(1, 2, 3)
        expected_neighbour = Point(1, 1, 3)
        got_neighbour = point.get_neighbour(Direction.NORTH)
        self.assertEqual(expected_neighbour, got_neighbour)

    def test_hash_same(self):
        point1 = Point(1, 2, 3)
        hash1 = point1.__hash__()
        point2 = Point(1, 2, 3)
        hash2 = point2.__hash__()
        self.assertEqual(hash1, hash2)

    def test_hash_not_same(self):
        point1 = Point(1, 2, 3)
        hash1 = point1.__hash__()
        point2 = Point(1, 3, 3)
        hash2 = point2.__hash__()
        self.assertNotEqual(hash1, hash2)

    def test_neighbour_south(self):
        point = Point(1, 2, 3)
        expected_neighbour = Point(1, 3, 3)
        got_neighbour = point.get_neighbour(Direction.SOUTH)
        self.assertEqual(expected_neighbour, got_neighbour)

    def test_neighbour_east(self):
        point = Point(1, 2, 3)
        expected_neighbour = Point(2, 2, 3)
        got_neighbour = point.get_neighbour(Direction.EAST)
        self.assertEqual(expected_neighbour, got_neighbour)

    def test_neighbour_west(self):
        point = Point(1, 2, 3)
        expected_neighbour = Point(0, 2, 3)
        got_neighbour = point.get_neighbour(Direction.WEST)
        self.assertEqual(expected_neighbour, got_neighbour)

    def test_neighbour_up(self):
        # Going up, z gets smaller.
        point = Point(1, 2, 3)
        expected_neighbour = Point(1, 2, 2)
        got_neighbour = point.get_neighbour(Direction.UP)
        self.assertEqual(expected_neighbour, got_neighbour)

    def test_neighbour_down(self):
        # Going down, z gets bigger.
        point = Point(1, 2, 3)
        expected_neighbour = Point(1, 2, 4)
        got_neighbour = point.get_neighbour(Direction.DOWN)
        self.assertEqual(expected_neighbour, got_neighbour)

    def test_all_neighbours_same_level(self):
        point = Point(1, 2, 3)
        all_neighbours = point.neighbours_same_level
        assert_that(all_neighbours).contains(Point(0, 2, 3))
        assert_that(all_neighbours).contains(Point(2, 2, 3))
        assert_that(all_neighbours).contains(Point(1, 1, 3))
        assert_that(all_neighbours).contains(Point(1, 3, 3))
