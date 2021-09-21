import unittest
from roguebot.navigation.direction import Direction


class TestDirection(unittest.TestCase):
    def test_north_int_value(self):
        self.assertEqual(1, Direction.NORTH.value)
