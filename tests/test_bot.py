
import unittest
from unittest import IsolatedAsyncioTestCase
import roguebot
from roguebot.bot import Bot
from roguebot.action import Action
from roguebot.brains.ibrain import IBrain
from roguebot.iclient import IEntityClient
from roguebot.state.dungeon_map import DungeonMap
from assertpy import assert_that
from unittest.mock import Mock, AsyncMock
from roguebot.state.state import State
from roguebot.navigation.direction import Direction
from roguebot.navigation.point import Point
from roguebot.state.entity import Entity, Entities
from tests.state.dungeon_draw import *

logging.basicConfig(level=logging.DEBUG)


class MockEntityClient(IEntityClient):
    def __init__(self, state: State = State()):
        self._state = state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state

    def set_bot(self, bot: Bot):
        pass

    def start_comms(self, async_client=None):
        """ starts talking to the server """
        pass

    def stop_comms(self):
        """ stops talking to the server """
        pass

    async def send_move(self, direction: Direction):
        """ sends a move to the server
        Normally, this will result in the position beingg updated
        """
        pass

    async def take_item(self, item_name: str):
        """ tells the server to take an item from the current location
        """
        pass

    async def eat_item(self, item_name: str):
        """ Tells the server to eat something from inventory """
        pass

    async def wear_item(self, item_name: str):
        """ Tells the server to wear something from inventory """
        pass

    async def wield_item(self, item_name: str):
        """ Tells the server to wield something from inventory """
        pass


class TestBot(unittest.TestCase):

    def test_can_create(self):
        character_name = "test_person"
        mock_client = MockEntityClient()
        Bot(character_name, mock_client)

    def test_can_get_out_state(self):
        state = State()
        bot = Bot("fred", MockEntityClient(state))
        state_got_back = bot.state
        assert_that(state_got_back).is_not_none().is_equal_to(state)

    def test_can_set_state(self):
        state1 = State()
        bot = Bot("fred", MockEntityClient(state1))
        state2 = State()
        bot.state = state2
        assert_that(bot.state).is_equal_to(state2)

    def test_got_enough_state_to_start_when_ok(self) -> None:
        picture = """
        ----------- level z=0 :
        ###
        # #
        # #
        ###
        -----------
        """
        dungeon = get_dungeon_from_picture(picture)

        state = State()
        state.my_entity_id = 'myId'
        me = Entity(char='@', name='me',
                    position=Point(1, 1, 0), identifier='myId')
        state.entities.add(me)
        state.dungeon_map = dungeon

        bot = Bot("me", MockEntityClient(state))

        assert_that(bot.got_enough_state_to_start()).is_true()

    def test_got_enough_state_to_start_when_no_dungeon_isnt_enough(self) -> None:
        state = State()
        state.my_entity_id = 'myId'
        me = Entity(char='@', name='me',
                    position=Point(1, 1, 0), identifier='myId')
        state.entities.add(me)

        bot = Bot("me", MockEntityClient(state))

        assert_that(bot.got_enough_state_to_start()).is_false()

    def test_got_enough_state_to_start_when_no_entity_id_isnt_enough(self) -> None:
        picture = """
        ----------- level z=0 :
        ###
        # #
        # #
        ###
        -----------
        """
        dungeon = get_dungeon_from_picture(picture)

        state = State()
        # Not set: state.my_entity_id = 'myId'
        me = Entity(char='@', name='me',
                    position=Point(1, 1, 0), identifier='myId2')
        state.entities.add(me)
        state.dungeon_map = dungeon

        bot = Bot("me", MockEntityClient(state))

        assert_that(bot.got_enough_state_to_start()).is_false()

    def test_got_enough_state_to_start_when_no_entity_for_myself_isnt_enough(self) -> None:

        state2 = State(entities=Entities())
        print("1 Entities in state:"+str(state2.entities))
        print("1 My entity id in state:"+str(state2.my_entity_id))

        picture = """
        ----------- level z=0 :
        ###
        # #
        # #
        ###
        -----------
        """
        dungeon = get_dungeon_from_picture(picture)
        state2.my_entity_id = 'myId'

        print("2 Entities in state:"+str(state2.entities))
        print("2 My entity id in state:"+str(state2.my_entity_id))

        state2.dungeon_map = dungeon

        print("3 Entities in state:"+str(state2.entities))
        print("3 My entity id in state:"+str(state2.my_entity_id))

        bot = Bot("me", MockEntityClient(state2))

        print("4 Entities in state:"+str(state2.entities))
        print("4 My entity id in state:"+str(state2.my_entity_id))

        assert_that(bot.got_enough_state_to_start()).is_false()

    def test_got_enough_state_to_start_when_no_state(self) -> None:
        bot = Bot("me", MockEntityClient(None))

        assert_that(bot.got_enough_state_to_start()).is_false()

    def test_clear_bot_with_brain_causes_clear_brain(self) -> None:
        mockBrain = Mock(spec=IBrain)
        bot = Bot("me", MockEntityClient(None))
        bot._brain = mockBrain
        bot.clear()

        mockBrain.clear.assert_called_once()

    def test_clear_bot_without_brain_does_nothing(self) -> None:
        bot = Bot("me", MockEntityClient(None))
        bot._brain = None
        bot.clear()  # Should not blow up.

    def test_status_summary_with_no_brain_doesnt_fail(self) -> None:
        bot = Bot("me", MockEntityClient(None))
        bot._brain = None
        summary = bot.status_summary
        assert_that(summary).is_empty()

    def test_status_summary_with_brain_returns_brain_status(self) -> None:
        mockBrain = Mock(spec=IBrain)
        brain_status = {'some': 'status'}
        mockBrain.status_summary = brain_status
        bot = Bot("me", MockEntityClient(None))
        bot._brain = mockBrain
        summary = bot.status_summary
        assert_that(summary).is_equal_to(brain_status)


class AsyncBotTest(IsolatedAsyncioTestCase):

    async def test_tick_does_nothing_when_ready_state_not_reached(self) -> None:

        class BotNotEverReady(Bot):
            def got_enough_state_to_start(self) -> bool:
                return False

        state = None
        bot = BotNotEverReady("me", MockEntityClient(state))
        bot._ignore_ticks_before_act = 1

        mock_brain = Mock(spec=IBrain)
        bot._brain = mock_brain
        mock_brain.decide_actions.return_value = []

        await bot.tick()
        mock_brain.decide_actions.assert_not_called()

    async def test_tick_doesnt_act_until_ignore_limit_reached(self) -> None:

        picture = """
        ----------- level z=0 :
        ###
        # #
        # #
        ###
        -----------
        """
        dungeon = get_dungeon_from_picture(picture)

        state = State()
        state.my_entity_id = 'myId'
        me = Entity(char='@', name='me',
                    position=Point(1, 1, 0), identifier='myId')
        state.entities.add(me)
        state.dungeon_map = dungeon

        bot = Bot("me", MockEntityClient(state))
        bot._ignore_ticks_before_act = 1

        mock_brain = Mock(spec=IBrain)
        bot._brain = mock_brain
        mock_brain.decide_actions.return_value = []

        # Should be ignored.
        await bot.tick()

        mock_brain.decide_actions.assert_not_called()

        await bot.tick()
        mock_brain.decide_actions.assert_called_once()

    async def test_action_returns_by_brain_gets_executed(self) -> None:
        mock_client = AsyncMock(spec=IEntityClient)
        bot = Bot("me", client=mock_client)
        mock_action = AsyncMock(spec=Action)
        mock_brain = Mock(spec=IBrain)
        bot._brain = mock_brain
        mock_brain.decide_actions.return_value = [mock_action]

        await bot._do_action()

        mock_action.do_action.assert_awaited_once()
