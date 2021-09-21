import roguebot
import re
import json
import logging
from roguebot.navigation.point import *
from roguebot.state.dungeon_map import *

# First lets trim every line, so pictures can be indented ok.


def trim_picture(picture):
    lines = picture.split("\n")
    trimmed_picture = ""
    for line in lines:
        trimmed_line = line.strip()
        if len(trimmed_line) != 0:
            trimmed_picture = trimmed_picture + trimmed_line + '\n'
    return trimmed_picture


def get_path_points_from_picture(picture: str) -> [Point]:
    """
    Given a picture of a route, return the list of points which form it.

    eg:
    __________
    #####
    #...#
    #  .#
    #####
    __________

    would return [ Point(1,1,0) , Point(2,1,0) , Point(3,1,0), Point(2,2,0) ]

    Note: The path points could be all mixed in order. 

    """
    trimmed_picture = trim_picture(picture)

    # Now split the input based on lines starting with '-' characters.
    z_parts = re.split("-[-]*.*\n", trimmed_picture)

    z = 0

    path_points = []

    for z_part in z_parts:
        if z_part is None or z_part == "":
            # Ignore
            pass
        else:
            y = 0
            # processing the z part.
            y_parts = z_part.split("\n")
            for y_part in y_parts:
                x = 0
                for c in y_part:
                    # print("Point({},{},{}) is {}".format(x, y, z, c))
                    if c == '.' or c == 'X':
                        path_points.append(Point(x, y, z))

                    x += 1
                y += 1
            z += 1

    return path_points


def get_dungeon_from_picture(picture: str, entrance=Point(99, 99, 99)) -> DungeonMap:
    """ Given a picture of the dungeon, render it to json which can be read as a dungeon.
    eg:
    ------
    ###
    # #
    # #
    ###
    ------

    ... is a single level dungeon. Where point 0,0,0 is a wall, and 1,1,0 is a dungeon floor.

    or

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

    ... which is a 2-level dungeon, with stairs going down from the top level '>' 
    and stairs going up at the bottom level '<'

    The origin is at the top-left corner.

    """

    def find_dimensions(picture):
        # Now split the input based on lines starting with '-' characters.
        z_parts = re.split("-[-]*.*\n", trimmed_picture)

        depth = len(z_parts)-2
        for z_part in z_parts:
            if z_part is None or z_part == "":
                # Ignore
                pass
            else:
                # processing the z part.
                y_parts = z_part.split("\n")
                height = len(y_parts)-1

                width = len(y_parts[0])
        return (width, height, depth)

    trimmed_picture = trim_picture(picture)

    (width, height, depth) = find_dimensions(trimmed_picture)

    dungeon = DungeonMap(height=height, depth=depth,
                         width=width, entrance=Point(99, 99, 99))

    # Now split the input based on lines starting with '-' characters.
    z_parts = re.split("-[-]*.*\n", trimmed_picture)

    z = 0

    for z_part in z_parts:
        if z_part is None or z_part == "":
            # Ignore
            pass
        else:
            y = 0
            # processing the z part.
            y_parts = z_part.split("\n")
            for y_part in y_parts:
                x = 0
                for c in y_part:
                    # print("Point({},{},{}) is {}".format(x, y, z, c))
                    if c == '#':
                        dungeon.set_cell(
                            Point(x, y, z), Cell.create_wall_cell())
                    elif c == ' ':
                        dungeon.set_cell(
                            Point(x, y, z), Cell.create_empty_cell())
                    elif c == '>':
                        dungeon.set_cell(
                            Point(x, y, z), Cell.create_stairs_cell('>'))
                    elif c == '<':
                        dungeon.set_cell(
                            Point(x, y, z), Cell.create_stairs_cell('<'))
                    elif c == 'O':
                        # print("Point is a gateway {}".format(Point(x, y, z)))
                        dungeon.set_cell(
                            Point(x, y, z), Cell.create_gateway_cell())

                    x += 1
                y += 1
            z += 1
    return dungeon
