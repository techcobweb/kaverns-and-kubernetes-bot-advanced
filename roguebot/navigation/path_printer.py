"""Tool for displaying a dungeon and path to follow in debug logging
"""

from ..state.dungeon_map import DungeonMap
from ..state.entity import Entity
from ..state.state import State
from .point import Point


class PathPrinter():
    """ Convenience functions to display the dungeon with a path of
    points, showing items and entities on a map during debugging.
    """

    def render_path(self, state: State,
                    path: [Point] = None,
                    only_show_floor: bool = False,
                    me_point: Point = None) -> str:
        """To help debugging, we can draw the dungeon, and overlay
        entities and a list of path points

        Parameters:
            state (State): The state of the world
            path ([Point]): A list of points, which will be plotted using '.' characters.
                It could show the planned route a goal is following.
            only_show_floor (bool): If true, only one floor is shown 
                (the one the me_point z value)
            me_point (Point): The coordinates of the 'me' entity, so we can show that as
                a X rather than '@' which all the other entities look like.

        Returns:
            str : The map, rendered as a multi-line string.

        The list of entities and dungeon map are taken from the passed
        state object

        Entities appear as '@' on the map.
        The path is a simple list of points, each appearing as a '.' character.

        Items appear as a '*'

        Stairs down are '>', stairs going up are '<'

        Gateways appears as 'O'

        For example:
        <pre>
        ######
        #.@  #
        #.   #
        #....#
        ####.#
        #....#
        #.@  #
        #    #
        ######
        </pre>

        ... which shows two entities '@' on the map, with a path being traced
        from a point in the top left corner of the top room, to the middle of
        the bottom room.
        """
        if path is None:
            path = []

        result = ''

        separator = ''
        for _ in range(state.dungeon_map.width):
            separator = separator + '-'

        result = result + "\n" + separator
        for z in range(state.dungeon_map.depth):
            if (only_show_floor is None) or (only_show_floor == z):
                for y in range(state.dungeon_map.height):
                    line = ""
                    for x in range(state.dungeon_map.width):
                        p = Point(x, y, z)

                        cell = state.dungeon_map.get_cell(p)

                        glyph = cell.char
                        if glyph == '.':
                            # We want dots to indicate a path we are following.
                            glyph = ' '

                        if cell.is_gateway:
                            glyph = 'O'

                        entity_there = state.entities.get_by_position(p)
                        if len(entity_there) > 0:
                            glyph = "@"

                        if path is not None and glyph == ' ':
                            if p in path:
                                glyph = "."

                        items_there = state.items.get_items_at_position(p)
                        if len(items_there) > 0:
                            glyph = '*'

                        if (me_point is not None) and (p == me_point):
                            glyph = 'X'

                        line = line + glyph
                    result = result + '\n' + line

                result = result + '\n' + separator
        result = result + '\n'
        return result
