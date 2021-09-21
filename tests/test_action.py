
import unittest
from roguebot.action import *
from roguebot.navigation.direction import *
from assertpy import assert_that
from unittest.mock import Mock
from unittest import IsolatedAsyncioTestCase


class MockEntityClient(IEntityClient):
    """ A mock for unit testing.
    """

    def __init__(self):
        self.move_direction = None
        self.take_item_name = None
        self.eat_item_name = None
        self.wear_item_name = None
        self.wield_item_name = None

    def start_comms(self, async_client=None):
        """ starts talking to the server """

    def stop_comms(self):
        """ stops talking to the server """

    async def send_move(self, direction: Direction):
        """ sends a move to the server
        Normally, this will result in the position beingg updated
        """
        self.move_direction = direction

    async def take_item(self, item_name: str):
        """ tells the server to take an item from the current location
        """
        self.take_item_name = item_name

    async def eat_item(self, item_name: str):
        """ Tells the server to eat something from inventory """
        self.eat_item_name = item_name

    async def wear_item(self, item_name: str):
        """ Tells the server to wear something from inventory """
        self.wear_item_name = item_name

    async def wield_item(self, item_name: str):
        """ Tells the server to wield something from inventory """
        self.wield_item_name = item_name


class TestAsyncMoveActionCalls(IsolatedAsyncioTestCase):

    async def test_do_action_calls_client_send_move_north(self):
        move_action = MoveAction(Direction.NORTH)
        mock_client = MockEntityClient()

        await move_action.do_action(mock_client)

        assert_that(mock_client.move_direction).is_equal_to(Direction.NORTH)

    async def test_do_action_calls_client_send_move_south(self):
        move_action = MoveAction(Direction.SOUTH)
        mock_client = MockEntityClient()

        await move_action.do_action(mock_client)

        assert_that(mock_client.move_direction).is_equal_to(Direction.SOUTH)


class TestMoveAction(unittest.TestCase):

    def test_can_create_a_move_action(self):
        move_action = MoveAction(Direction.NORTH)
        assert_that(move_action.direction).is_equal_to(Direction.NORTH)
        assert_that(move_action.action_code).is_equal_to(ActionCode.MOVE)

    def test_move_action_to_string(self):
        move_action = MoveAction(Direction.NORTH)
        assert_that(str(move_action)).contains("NORTH").contains("MoveAction")

    def test_move_action_repr(self):
        move_action = MoveAction(Direction.NORTH)
        assert_that(str([move_action])).contains(
            "NORTH").contains("MoveAction")


class TestTakeAction(unittest.TestCase):
    def test_take_action_to_string(self):
        take_action = TakeAction("banana")
        assert_that(str(take_action)).contains("banana").contains("TakeAction")

    def test_take_action_can_get_back_item_name(self):
        take_action = TakeAction("banana")
        assert_that(take_action.item_name).is_equal_to("banana")

    def test_code(self):
        action = TakeAction("hat")
        assert_that(action.action_code).is_equal_to(ActionCode.TAKE)


class TestAsyncTakeActionCalls(IsolatedAsyncioTestCase):

    async def test_take_hat_action(self):
        take_action = TakeAction("hat")
        mock_client = MockEntityClient()

        await take_action.do_action(mock_client)

        assert_that(mock_client.take_item_name).is_equal_to("hat")


class TestEatAction(unittest.TestCase):
    def test_can_set_and_get_item_name(self):
        action = EatAction("hat")
        assert_that(action.item_name).is_equal_to("hat")

    def test_str_renders_eat(self):
        action = EatAction("hat")
        assert_that(str(action)).contains("Eat")

    def test_code(self):
        action = EatAction("hat")
        assert_that(action.action_code).is_equal_to(ActionCode.EAT)

    def test_str(self):
        action = EatAction("hat")
        assert_that(str(action)).contains("Eat").contains("hat")

    def test_repr(self):
        action = EatAction("hat")
        action_list = [action]
        assert_that(str(action_list)).contains("Eat").contains("hat")


class TestAsyncEatActionCalls(IsolatedAsyncioTestCase):

    async def test_take_hat_action(self):
        eat_action = EatAction("cake")
        mock_client = MockEntityClient()

        await eat_action.do_action(mock_client)

        assert_that(mock_client.eat_item_name).is_equal_to("cake")


class TestWearAction(unittest.TestCase):
    def test_can_set_and_get_item_name(self):
        action = WearAction("hat")
        assert_that(action.item_name).is_equal_to("hat")

    def test_str_renders_wear(self):
        action = WearAction("hat")
        assert_that(str(action)).contains("Wear")

    def test_code(self):
        action = WearAction("hat")
        assert_that(action.action_code).is_equal_to(ActionCode.WEAR)


class TestAsyncWearActionCalls(IsolatedAsyncioTestCase):

    async def test_take_hat_action(self):
        wear_action = WearAction("trousers")
        mock_client = MockEntityClient()

        await wear_action.do_action(mock_client)

        assert_that(mock_client.wear_item_name).is_equal_to("trousers")


class TestWieldAction(unittest.TestCase):
    def test_can_set_and_get_item_name(self):
        action = WieldAction("hat")
        assert_that(action.item_name).is_equal_to("hat")

    def test_str_renders_wield(self):
        action = WieldAction("hat")
        assert_that(str(action)).contains("Wield")

    def test_code(self):
        action = WieldAction("hat")
        assert_that(action.action_code).is_equal_to(ActionCode.WIELD)


class TestAsyncWearActionCalls(IsolatedAsyncioTestCase):

    async def test_take_hat_action(self):
        wear_action = WearAction("trousers")
        mock_client = MockEntityClient()

        await wear_action.do_action(mock_client)

        assert_that(mock_client.wear_item_name).is_equal_to("trousers")


if __name__ == '__main__':
    unittest.main()
