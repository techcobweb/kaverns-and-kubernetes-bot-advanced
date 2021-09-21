
import unittest
import roguebot
from assertpy import assert_that
from roguebot.navigation.point import Point
from roguebot.state.cell import Cell


class TestCell(unittest.TestCase):
    def get_simple_input(self):
        input = {'char': '#', 'foreground': 'goldenrod', 'background': 'black', 'walkable': True, 'diggable': True, 'blocksLight': True, 'gateway': False, 'description': 'A cave wall'
                 }
        return input

    def get_gateway_input(self):
        input = {'char': 'O', 'walkable': True, 'diggable': True, 'blocksLight': True,
                 'gateway': False, 'description': 'A gateway to a strange place'}
        return input

    def test_extracts_char_from_wire_formatt_ok(self):
        input = self.get_simple_input()
        cell = Cell.from_wire_format(input)
        assert_that(cell.char).is_equal_to('#')
        assert_that(str(cell)).is_equal_to('#')

    def test_is_walkable_parsed_from_wire_format_ok(self):
        input = self.get_simple_input()
        cell = Cell.from_wire_format(input)
        self.assertEqual(True, cell.is_walkable())

    def test_cell_can_store_and_get_back_a_point(self):
        input = self.get_simple_input()
        cell = Cell.from_wire_format(input)
        self.assertEqual(None, cell.position)
        cell.position = Point(1, 2, 3)
        self.assertEqual(Point(1, 2, 3), cell.position)

    def test_can_create_gateway_cell(self):
        cell = Cell.create_gateway_cell()
        assert_that(cell.is_gateway).is_true()

    def test_can_parse_gateway_from_wire_format(self):
        input = self.get_gateway_input()
        cell = Cell.from_wire_format(input)

        assert_that(cell.is_gateway).is_true()


if __name__ == '__main__':
    unittest.main()
