import unittest
import roguebot
import logging
from roguebot.navigation.point import *
from roguebot.state.dungeon_map import *
from assertpy import assert_that
import re
import json
from tests.state.dungeon_draw import *

logging.basicConfig(level=logging.DEBUG)


class TestDungeonMap(unittest.TestCase):

    def test_get_dungeon_from_picture(self):
        picture = """
        ----------- level z=0 :
        ###
        # #
        # #
        ###
        -----------
        """
        dungeon = get_dungeon_from_picture(picture)
        assert_that(dungeon.height).is_equal_to(4)
        assert_that(dungeon.depth).is_equal_to(1)
        assert_that(dungeon.width).is_equal_to(3)
        assert_that(dungeon.get_cell(Point(0, 0, 0)).char).is_equal_to('#')
        assert_that(dungeon.get_cell(Point(1, 1, 0)).char).is_equal_to(' ')

    def test_dungeon_has_no_exit(self):
        picture = """
        ----------- level z=0 :
        ####
        #  #
        #  #
        ####
        -----------
        """
        dungeon = get_dungeon_from_picture(picture)
        assert_that(dungeon.gateway_points).is_empty()

    def test_dungeon_has_one_exit(self):
        picture = """
        ----------- level z=0 :
        ####
        #  #
        # O#
        ####
        -----------
        """
        dungeon = get_dungeon_from_picture(picture)
        assert_that(dungeon.gateway_points).is_not_none().is_length(
            1).contains(Point(2, 2, 0))

    def test_dungeon_has_two_exits(self):
        picture = """
        ----------- level z=0 :
        ####
        #  #
        #OO#
        ####
        -----------
        """
        dungeon = get_dungeon_from_picture(picture)
        assert_that(dungeon.gateway_points).is_not_none().is_length(
            2).contains(Point(2, 2, 0)).contains(Point(1, 2, 0))

    def get_simple_input(self):
        input = {
            'width': 2, 'height': 2, 'depth': 3,
            'tiles': [
                [  # First level. z=0
                    [
                        {'char': '#', 'foreground': 'goldenrod', 'background': 'black',
                         'walkable': False, 'diggable': True, 'blocksLight': True,
                         'gateway': False, 'description': 'A cave wall'
                         },
                        {'char': '#', 'foreground': 'goldenrod', 'background': 'black',
                         'walkable': False, 'diggable': True, 'blocksLight': True,
                         'gateway': False, 'description': 'A cave wall'
                         }
                    ],
                    [
                        {'char': '#', 'foreground': 'goldenrod', 'background': 'black',
                         'walkable': False, 'diggable': True, 'blocksLight': True,
                         'gateway': False, 'description': 'A cave wall'
                         },
                        {'char': ' ', 'foreground': 'black', 'background': 'black',
                         'walkable': True, 'diggable': True, 'blocksLight': False,
                         'gateway': False, 'description': 'A cave floor'
                         }
                    ]
                ],
                [  # Second level. z=1
                    [
                        {'char': '#', 'foreground': 'goldenrod', 'background': 'black',
                         'walkable': False, 'diggable': True, 'blocksLight': True,
                         'gateway': False, 'description': 'A cave wall'
                         },
                        {'char': '#', 'foreground': 'goldenrod', 'background': 'black',
                         'walkable': False, 'diggable': True, 'blocksLight': True,
                         'gateway': False, 'description': 'A cave wall'
                         }
                    ],
                    [  # < up-stairs. x=0,y=1,z=1
                        {'char': '<', 'foreground': 'goldenrod', 'background': 'black',
                         'walkable': True, 'diggable': False, 'blocksLight': True,
                         'gateway': False, 'description': 'stairs up'
                         },
                        {'char': ' ', 'foreground': 'black', 'background': 'black',
                         'walkable': True, 'diggable': True, 'blocksLight': False,
                         'gateway': False, 'description': 'A cave floor'
                         }
                    ]
                ],
                [  # Third level. z=2
                    [
                        {'char': '#', 'foreground': 'goldenrod', 'background': 'black',
                         'walkable': False, 'diggable': True, 'blocksLight': True,
                         'gateway': False, 'description': 'A cave wall'
                         },
                        {'char': '#', 'foreground': 'goldenrod', 'background': 'black',
                         'walkable': False, 'diggable': True, 'blocksLight': True,
                         'gateway': False, 'description': 'A cave wall'
                         }
                    ],
                    [   # Down-stairs x=0,y=1,z=2
                        {'char': '<', 'foreground': 'goldenrod', 'background': 'black',
                         'walkable': True, 'diggable': False, 'blocksLight': True,
                         'gateway': False, 'description': 'Down stairs'
                         },
                        {'char': ' ', 'foreground': 'black', 'background': 'black',
                         'walkable': True, 'diggable': True, 'blocksLight': False,
                         'gateway': False, 'description': 'A cave floor'
                         }
                    ]
                ]
            ],
            'entrance': {'x': 1, 'y': 1, 'z': 0}
        }
        return input

    def test_extracts_dimensions(self):
        input = self.get_simple_input()
        dungeon = DungeonMap.from_wire_format(input)
        self.assertEqual(2, dungeon.height)
        self.assertEqual(3, dungeon.depth)
        self.assertEqual(2, dungeon.width)

    def test_get_wall_outside_dimensions(self):
        picture = """
        ----------- level z=0 :
        ###
        # #
        # #
        ###
        -----------
        """
        dungeon = get_dungeon_from_picture(picture)
        assert_that(dungeon.get_cell(Point(60, 60, 0)).char).is_equal_to('#')

    def test_extracts_entrance(self):
        input = self.get_simple_input()
        dungeon = DungeonMap.from_wire_format(input)
        self.assertEqual(Point(1, 1, 0), dungeon.entrance)

    def test_extracts_cells(self):
        input = self.get_simple_input()
        dungeon = DungeonMap.from_wire_format(input)
        self.assertEqual('#', dungeon.get_cell(Point(1, 0, 0)).char)
        self.assertEqual(' ', dungeon.get_cell(Point(1, 1, 0)).char)
        self.assertEqual('<', dungeon.get_cell(Point(0, 1, 2)).char)

    def test_is_walkable_can_return_true(self):
        input = self.get_simple_input()
        dungeon = DungeonMap.from_wire_format(input)
        point = Point(1, 1, 0)
        expected = True
        got_back = dungeon.is_walkable(point)
        self.assertEqual(expected, got_back)

    def test_is_walkable_can_return_false(self):
        input = self.get_simple_input()
        dungeon = DungeonMap.from_wire_format(input)
        point = Point(0, 0, 0)
        expected = False
        got_back = dungeon.is_walkable(point)
        self.assertEqual(expected, got_back)

    def test_is_walkable_too_far_north(self):
        input = self.get_simple_input()
        dungeon = DungeonMap.from_wire_format(input)
        point = Point(0, -1, 0)
        expected = False
        got_back = dungeon.is_walkable(point)
        self.assertEqual(expected, got_back)

    def test_is_walkable_too_far_south(self):
        input = self.get_simple_input()
        dungeon = DungeonMap.from_wire_format(input)
        point = Point(0, 15, 0)
        expected = False
        got_back = dungeon.is_walkable(point)
        self.assertEqual(expected, got_back)

    def get_simple_small_square_room_no_entrance(self):
        input = {
            'width': 2, 'height': 2, 'depth': 1,
            'tiles': [
                [  # First level. z=0
                    [
                        {'char': ' ', 'foreground': 'goldenrod', 'background': 'black',
                         'walkable': True, 'diggable': True, 'blocksLight': True,
                         'gateway': False, 'description': 'A cave wall'
                         },
                        {'char': ' ', 'foreground': 'goldenrod', 'background': 'black',
                         'walkable': True, 'diggable': True, 'blocksLight': True,
                         'gateway': False, 'description': 'A cave wall'
                         }
                    ],
                    [
                        {'char': ' ', 'foreground': 'goldenrod', 'background': 'black',
                         'walkable': True, 'diggable': True, 'blocksLight': True,
                         'gateway': True, 'description': 'A cave wall'
                         },
                        {'char': ' ', 'foreground': 'black', 'background': 'black',
                         'walkable': True, 'diggable': True, 'blocksLight': False,
                         'gateway': False, 'description': 'A cave floor'
                         }
                    ]
                ]
            ],
            # Entrance is miles away so we don't need to consider it,
            'entrance': {'x': 1, 'y': 1, 'z': 15}
        }
        return input

    def test_bottom_left_corner_neighbours(self):
        picture = """
            ----------- level z=0 : top of dungeon: origin is top-left corner.
            ####
            #  #
            #  #
            ####
            -----------
            """
        dungeon = get_dungeon_from_picture(picture)

        point = Point(1, 1, 0)
        neighbours = dungeon.get_neighbour_points(point)
        assert_that(neighbours).is_length(2).contains(
            Point(1, 2, 0)).contains(Point(2, 1, 0))

    def test_top_right_corner(self):
        picture = """
            ----------- level z=0 : origin is top-left corner.
            ####
            #  #
            #  #
            ####
            -----------
            """
        dungeon = get_dungeon_from_picture(picture)
        point = Point(2, 1, 0)
        neighbours = dungeon.get_neighbour_points(point)
        assert_that(neighbours).is_length(2).contains(
            Point(2, 2, 0)).contains(Point(1, 1, 0))

    def test_neighbours_can_be_below(self):
        picture = """
            ----------- level z=0 : top of dungeon: origin is top-left corner.
            ####
            # >#
            #  #
            ####
            ----------- level z=1: one level down:
            ####
            # <#
            #  #
            ####
            -----------
            """
        dungeon = get_dungeon_from_picture(picture)
        # Sit a point on the top of the stairs going down to the next level...
        point = Point(2, 1, 0)

        neighbours = dungeon.get_neighbour_points(point)

        assert_that(neighbours).is_length(3).contains(
            Point(1, 1, 0)).contains(
                Point(2, 2, 0)).contains(Point(2, 1, 1))

    def test_neighbours_can_be_above(self):
        picture = """
            ----------- level z=0 : top of dungeon: origin is top-left corner.
            ####
            # >#
            #  #
            ####
            ----------- level z=1: one level down:
            ####
            # <#
            #  #
            ####
            -----------
            """
        dungeon = get_dungeon_from_picture(picture)
        # Sit a point on the bottom of the stairs going up to the top level...
        point = Point(2, 1, 1)

        neighbours = dungeon.get_neighbour_points(point)
        assert_that(neighbours).is_length(3).contains(
            Point(2, 2, 1)).contains(
                Point(1, 1, 1)).contains(Point(2, 1, 0))

    def test_neighbours_ignores_entrance(self):
        picture = """
            ----------- level z=0 : top of dungeon: origin is top-left corner.
            ###
            # #
            ###
            -----------
            """
        dungeon = get_dungeon_from_picture(picture, Point(1, 1, 0))
        point = Point(1, 1, 0)

        neighbours = dungeon.get_neighbour_points(point)

        # The entrance can't be considered a neighbour.
        assert_that(neighbours).is_length(0)

    def test_setting_cell_outside_dungeon_dimensions_is_ignored(self):
        picture = """
            ----------- level z=0 : top of dungeon: origin is top-left corner.
            ###
            # #
            ###
            -----------
            """
        dungeon = get_dungeon_from_picture(picture, Point(1, 1, 0))
        dungeon.set_cell(Point(50, 50, 50), Cell("?", is_walkable=False))
        # Didn't blow up, so that's all we can say.

    def test_can_set_and_get_entrance(self):
        picture = """
            ----------- level z=0 : top of dungeon: origin is top-left corner.
            ###
            # #
            ###
            -----------
            """
        dungeon = get_dungeon_from_picture(picture, Point(1, 1, 0))
        dungeon.entrance = Point(1, 1, 0)
        assert_that(dungeon.entrance).is_equal_to(Point(1, 1, 0))

    def test_can_get_all_up_staors(self):
        # Map only has down stairs.
        picture = """
            ----------- level z=0 : top of dungeon: origin is top-left corner.
            #####
            #  >#
            #>  #
            #####
            -----------
            """
        dungeon = get_dungeon_from_picture(picture, Point(1, 1, 0))

        stair_points = dungeon.get_stair_points(
            z_dungeon_level=0, direction=Direction.DOWN)
        assert_that(stair_points).is_length(2).contains(
            Point(1, 2, 0)).contains(Point(3, 1, 0))

    def test_can_get_all_up_stairs(self):
        # Map only has down stairs.
        picture = """
            ----------- level z=0 : top of dungeon: origin is top-left corner.
            #####
            #  <#
            #<  #
            #####
            -----------
            """
        dungeon = get_dungeon_from_picture(picture, Point(1, 1, 0))

        stair_points = dungeon.get_stair_points(
            z_dungeon_level=0, direction=Direction.UP)
        assert_that(stair_points).is_length(2).contains(
            Point(1, 2, 0)).contains(Point(3, 1, 0))

    def test_can_get_all_up_stairs_level_too_low(self):
        # Map only has down stairs.
        picture = """
            ----------- level z=0 : top of dungeon: origin is top-left corner.
            #####
            #  <#
            #<  #
            #####
            -----------
            """
        dungeon = get_dungeon_from_picture(picture, Point(1, 1, 0))

        stair_points = dungeon.get_stair_points(
            z_dungeon_level=-1, direction=Direction.UP)

        # We don't expect any points from there.
        assert_that(stair_points).is_length(0)

    def test_can_get_all_up_stairs_level_too_high(self):
        # Map only has down stairs.
        picture = """
            ----------- level z=0 : top of dungeon: origin is top-left corner.
            #####
            #  <#
            #<  #
            #####
            -----------
            """
        dungeon = get_dungeon_from_picture(picture, Point(1, 1, 0))

        stair_points = dungeon.get_stair_points(
            z_dungeon_level=20, direction=Direction.UP)

        # We don't expect any points from there.
        assert_that(stair_points).is_length(0)

    def test_cant_find_stairs_heading_east(self):
        # Map only has down stairs.
        picture = """
            ----------- level z=0 : top of dungeon: origin is top-left corner.
            #####
            #  <#
            #<  #
            #####
            -----------
            """
        dungeon = get_dungeon_from_picture(picture, Point(1, 1, 0))

        # East is an invalid direction to look for stairs...
        stair_points = dungeon.get_stair_points(
            z_dungeon_level=0, direction=Direction.EAST)

        # We don't expect any points from there.
        assert_that(stair_points).is_length(0)

    def test_can_get_all_up_stairs_level_bad_direction(self):
        # Map only has down stairs.
        picture = """
            ----------- level z=0 : top of dungeon: origin is top-left corner.
            #####
            #  <#
            #<  #
            #####
            -----------
            """
        dungeon = get_dungeon_from_picture(picture, Point(1, 1, 0))

        stair_points = dungeon.get_stair_points(
            z_dungeon_level=20, direction=Direction.EAST)

        # We don't expect any points from there.
        assert_that(stair_points).is_length(0)


if __name__ == '__main__':
    unittest.main()
