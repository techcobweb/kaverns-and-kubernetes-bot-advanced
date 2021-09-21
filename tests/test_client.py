
import pytest
from unittest import IsolatedAsyncioTestCase
from roguebot.bot import Bot
from roguebot.client import EntityClient
from assertpy import assert_that
from unittest.mock import Mock
from roguebot.state.state import State
from roguebot.state.item import Items
from roguebot.state.entity import Entity, Entities
from roguebot.navigation.direction import Direction
from roguebot.navigation.point import Point


class MockSocketIO():

    def __init__(self):
        self.events_registered = list()
        self.is_disconnect_called = False
        self.emitted_event_name = None
        self.emitted_event_data = None
        self.identifier = "abc-identifier"

    def on(self, event_name: str, callback) -> None:
        self.events_registered.append(event_name)

    async def connect(self, url, auth, transports, socketio_path=None) -> None:
        pass

    async def wait(self) -> None:
        pass

    async def disconnect(self) -> None:
        self.is_disconnect_called = True

    async def emit(self, event_name: str, data=None) -> None:
        self.emitted_event_name = event_name
        self.emitted_event_data = data

    def get_sid(self) -> str:
        return self.identifier


class MockBot():
    def __init__(self):
        self.is_tick_called = False

    async def tick(self):
        self.is_tick_called = True


@pytest.fixture
def socket_io():
    return MockSocketIO()


@pytest.fixture
def entity_client():
    return EntityClient(character_name="fred",
                        character_role="warrior",
                        url="http://localhost:2999"
                        )


def test_events_are_registered_with_callbacks_when_comms_starts(entity_client) -> None:
    socket_io = MockSocketIO()

    entity_client.start_comms(socket_io)

    assert_that(socket_io.events_registered) \
        .contains("connect") \
        .contains("connect_error") \
        .contains("missing_role") \
        .contains("map") \
        .contains("disconnect") \
        .contains("entities") \
        .contains("ping") \
        .contains("*") \
        .contains("items") \
        .contains("position") \
        .contains("dead") \
        .contains("delete") \
        .contains("message") \
        .contains("update") \
        .contains("reconnect")
    assert_that(socket_io.events_registered).is_length(15)


class TestAsyncClientCalls(IsolatedAsyncioTestCase):

    async def test_connect_error_event_gets_handled(self) -> None:
        entity_client = EntityClient(character_name="fred",
                                     character_role="warrior",
                                     url="http://localhost:2999"
                                     )

        rc = await entity_client.connect_error("some data to log")
        assert_that(rc).is_false()

    async def test_disconnect_event_gets_handled(self) -> None:
        entity_client = EntityClient(character_name="fred",
                                     character_role="warrior",
                                     url="http://localhost:2999"
                                     )

        rc = await entity_client.disconnect_received()
        assert_that(rc).is_false()

    async def test_other_event_gets_handled(self) -> None:
        entity_client = EntityClient(character_name="fred",
                                     character_role="warrior",
                                     url="http://localhost:2999"
                                     )

        await entity_client.other_event_received()

        # Didn't blow up if it got this far. Good.

    async def test_missing_role_event_gets_handled(self) -> None:
        entity_client = EntityClient(character_name="fred",
                                     character_role="warrior",
                                     url="http://localhost:2999"
                                     )

        await entity_client.missing_role_received()

    async def test_dead_event_disconnects_from_web_socket(self) -> None:
        entity_client = EntityClient(character_name="fred",
                                     character_role="warrior",
                                     url="http://localhost:2999"
                                     )
        socket_io = MockSocketIO()
        entity_client._sio = socket_io

        await entity_client.dead_received("faking bot death")

        assert_that(socket_io.is_disconnect_called).is_true()

    async def test_send_move_emits_correct_output(self) -> None:
        entity_client = EntityClient(character_name="fred",
                                     character_role="warrior",
                                     url="http://localhost:2999"
                                     )
        socket_io = MockSocketIO()
        entity_client._sio = socket_io

        await entity_client.send_move(Direction.NORTH)

        assert_that(socket_io.emitted_event_name).is_equal_to("move")
        assert_that(socket_io.emitted_event_data).is_equal_to("NORTH")

    async def test_take_item_emits_correct_output(self) -> None:
        entity_client = EntityClient(character_name="fred",
                                     character_role="warrior",
                                     url="http://localhost:2999"
                                     )
        socket_io = MockSocketIO()
        entity_client._sio = socket_io

        await entity_client.take_item("hat")

        assert_that(socket_io.emitted_event_name).is_equal_to("take")
        assert_that(socket_io.emitted_event_data).is_equal_to("hat")

    async def test_eat_item_emits_correct_output(self) -> None:
        entity_client = EntityClient(character_name="fred",
                                     character_role="warrior",
                                     url="http://localhost:2999"
                                     )
        socket_io = MockSocketIO()
        entity_client._sio = socket_io

        await entity_client.eat_item("hat")

        assert_that(socket_io.emitted_event_name).is_equal_to("eat")
        assert_that(socket_io.emitted_event_data).is_equal_to("hat")

    async def test_wear_item_emits_correct_output(self) -> None:
        entity_client = EntityClient(character_name="fred",
                                     character_role="warrior",
                                     url="http://localhost:2999"
                                     )
        socket_io = MockSocketIO()
        entity_client._sio = socket_io

        await entity_client.wear_item("hat")

        assert_that(socket_io.emitted_event_name).is_equal_to("wear")
        assert_that(socket_io.emitted_event_data).is_equal_to("hat")

    async def test_ping_received_ticks_the_bot(self):
        entity_client = EntityClient(character_name="fred",
                                     character_role="warrior",
                                     url="http://localhost:2999"
                                     )
        mock_bot = MockBot()
        entity_client._bot = mock_bot

        await entity_client.ping_received()

        assert_that(mock_bot.is_tick_called).is_true()

    async def test_connect_received_sets_entity_id(self):
        entity_client = EntityClient(character_name="fred",
                                     character_role="warrior",
                                     url="http://localhost:2999"
                                     )

        socket_io = MockSocketIO()
        entity_client._sio = socket_io

        state = State()
        entity_client._state = state

        await entity_client.connect_received()

        assert_that(state.my_entity_id).is_equal_to("abc-identifier")
        assert_that(socket_io.emitted_event_name).is_equal_to("get_map")
        assert_that(socket_io.emitted_event_data).is_none()

    async def test_update_received_updates_state(self):
        entity_client = EntityClient(character_name="fred",
                                     character_role="warrior",
                                     url="http://localhost:2999"
                                     )

        socket_io = MockSocketIO()
        entity_client._sio = socket_io

        state = State()
        entity_client._state = state

        entity = Entity("A", "mc", Point(1, 1, 0), "aaa")
        entities = Entities()
        entities.add(entity)
        state._entities = entities

        raw_entity_wire_format_data = {'char': '@', 'foreground': 'yellow', 'background': 'black',
                                       'alive': True, 'walkable': True,
                                       'pos': {'x': 31, 'y': 16, 'z': 0},
                                       'name': 'mc', 'details': 'a brawny warrior',
                                       'edible': False,
                                       'wieldable': False, 'wearable': False,
                                       'id': 'aaa', 'role': 'warrior',
                                       'type': 'player', 'level': 0,
                                       'speed': 1000, 'maxHitPoints': 10,
                                       'hitPoints': 10,
                                       'hunger': 0,
                                       'sight': 10, 'currentArmour': None, 'currentWeapon': None,
                                       'ac': 10, 'inventory': []
                                       }

        await entity_client.update_received(raw_entity_wire_format_data)

        entity_set_into_state = state.entities.get_by_id("aaa")

        assert_that(entity_set_into_state.position).is_equal_to(
            Point(31, 16, 0))

    async def test_position_received_updates_entity(self):
        entity_client = EntityClient(character_name="fred",
                                     character_role="warrior",
                                     url="http://localhost:2999"
                                     )
        state = State()
        entity_client._state = state

        entity = Entity("A", "mc", Point(1, 1, 0), "aaa")
        entities = Entities()
        entities.add(entity)
        state._entities = entities

        raw_wire_format_data = {'id': 'aaa', "pos": {'x': 1, 'y': 2, 'z': 0}}

        await entity_client.position_received(raw_wire_format_data)

        entity_set_into_state = state.entities.get_by_id("aaa")

        # The entity position should have changed.
        assert_that(entity_set_into_state.position).is_equal_to(
            Point(1, 2, 0))

    async def test_delete_received_updates_state(self):
        entity_client = EntityClient(character_name="fred",
                                     character_role="warrior",
                                     url="http://localhost:2999"
                                     )

        socket_io = MockSocketIO()
        entity_client._sio = socket_io

        state = State()
        entity_client._state = state

        entity = Entity("@", "mc", Point(1, 1, 0), "aaa")
        entities = Entities()
        entities.add(entity)
        state._entities = entities

        delete_event_wire_data = {'char': '@', 'foreground': 'yellow', 'background': 'black',
                                  'alive': True, 'walkable': True,
                                  'pos': {'x': 1, 'y': 1, 'z': 0},
                                  'name': 'mc', 'details': 'a brawny warrior',
                                  'edible': False,
                                  'wieldable': False, 'wearable': False,
                                  'id': 'aaa', 'role': 'warrior',
                                  'type': 'player', 'level': 0,
                                  'speed': 1000, 'maxHitPoints': 10,
                                  'hitPoints': 10,
                                  'hunger': 0,
                                  'sight': 10, 'currentArmour': None, 'currentWeapon': None,
                                  'ac': 10, 'inventory': [],
                                  'corpse': {'char': '%', 'foreground': 'red', 'background': 'black',
                                             'alive': False, 'walkable': True}, 'pos': {'x': 0, 'y': 0, 'z': 0},
                                  'rules': {}, 'damage': 1, 'hitBonus': 1, 'base_ac': 10,
                                  'entrance': {'x': 31, 'y': 16, 'z': 0}
                                  }

        await entity_client.delete_received(delete_event_wire_data)

        entity_set_into_state = state.entities.get_by_id("aaa")

        # It should have gone from our state.
        assert_that(entity_set_into_state).is_none()


class TestClient(IsolatedAsyncioTestCase):

    def test_can_join_network_with_game(self):
        client = EntityClient(character_name="fred",
                              character_role="warrior",
                              url="http://localhost:2999"
                              )
        bot = Bot(character_name="fred", client=client)
        assert_that(client.bot).is_equal_to(bot)

    async def test_can_update_items(self):
        client = EntityClient(character_name="fred",
                              character_role="warrior",
                              url="http://localhost:2999"
                              )

        client.state = State()

        entity = Entity("A", "mc", Point(1, 1, 0), "aaa")
        entities = Entities()
        entities.add(entity)
        client.state.entities = entities

        client.state.my_entity_id = "aaa"

        items = Mock(spec=Items)
        client.state._items = items

        item_wire_format_data = {'(22,16,0)': [
            {'char': 'o',
             'pos': {'x': 22, 'y': 16, 'z': 0},
             'name': 'apple',
             'edible': True,
             'wieldable': False,
             'wearable': False
             }
        ]
        }
        result = await client.items_received(item_wire_format_data)

        items.update_items.assert_called()

    async def test_can_update_map(self):
        # Given...
        client = EntityClient(character_name="fred",
                              character_role="warrior",
                              url="http://localhost:2999"
                              )
        state = Mock(State)
        client.state = state
        wire_map_data = {
            'width': 1, 'height': 1, 'depth': 1,
            'tiles': [
                [  # First level. z=0
                    [
                        {'char': '#', 'foreground': 'goldenrod', 'background': 'black',
                         'walkable': False, 'diggable': True, 'blocksLight': True,
                         'gateway': False, 'description': 'A cave wall'
                         }
                    ]
                ]
            ],
            'entrance': {'x': 0, 'y': 0, 'z': 0}
        }

        # When...
        result = await client.map_received(wire_map_data)

        # Then ... bot should now have a dungeon map created from the wire-data.
        assert_that(state.dungeon_map.width).is_equal_to(1)
        assert_that(state.dungeon_map.depth).is_equal_to(1)
        assert_that(state.dungeon_map.height).is_equal_to(1)

    async def test_client_accumulates_messages(self):
        client = EntityClient(character_name="fred",
                              character_role="warrior",
                              url="http://localhost:2999"
                              )
        wire_message_data = "a message"

        # When...
        result = await client.message_received(wire_message_data)

        # Then ... bot should now have a dungeon map created from the wire-data.
        assert_that(client.state.messages.pop(0)).is_equal_to("a message")

    async def test_client_entities_received(self):
        client = EntityClient(character_name="fred",
                              character_role="warrior",
                              url="http://localhost:2999"
                              )

        entity = Entity("A", "mc", Point(1, 1, 0), "aaa")
        entities = Entities()
        entities.add(entity)
        client.state.entities = entities

        client.state.my_entity_id = "aaa"

        raw_entity_wire_format_data = [{'char': '@', 'foreground': 'yellow', 'background': 'black',
                                       'alive': True, 'walkable': True,
                                        'pos': {'x': 31, 'y': 16, 'z': 0},
                                        'name': 'newName', 'details': 'a brawny warrior',
                                        'edible': False,
                                        'wieldable': False, 'wearable': False,
                                        'id': 'aaa', 'role': 'warrior',
                                        'type': 'player', 'level': 0,
                                        'speed': 1000, 'maxHitPoints': 10,
                                        'hitPoints': 10,
                                        'hunger': 0,
                                        'sight': 10, 'currentArmour': None, 'currentWeapon': None,
                                        'ac': 10, 'inventory': []
                                        }]

        # When...
        result = await client.entities_received(raw_entity_wire_format_data)

        # Then ... bot should now have a dungeon map created from the wire-data.
        assert_that(client.state.entities.get_by_id(
            'aaa').name).is_equal_to("newName")

    async def test_client_reconnect_received_sent_complete_url(self):

        client = StopNoOpClient(character_name="fred",
                                character_role="warrior",
                                url="http://localhost:2999"
                                )

        raw_entity_wire_format_data = {'url': 'http://somewhere-else'}

        # When...
        result = await client.reconnect_received(raw_entity_wire_format_data)

        # Then ... bot should now have a dungeon map created from the wire-data.
        assert_that(client._server_url).is_equal_to("http://somewhere-else")
        assert_that(client._is_reconnecting).is_true()

    async def test_client_reconnect_received_sent_path_after_url(self):

        client = StopNoOpClient(character_name="fred",
                                character_role="warrior",
                                url="http://localhost:2999"
                                )

        raw_entity_wire_format_data = {'url': '/cake'}

        # When...
        result = await client.reconnect_received(raw_entity_wire_format_data)

        # Then ... bot should now have a dungeon map created from the wire-data.
        assert_that(client._server_url).is_equal_to(
            "http://localhost:2999/cake")
        assert_that(client._is_reconnecting).is_true()

    async def test_client_reconnect_received_sent_path_after_path(self):

        client = StopNoOpClient(character_name="fred",
                                character_role="warrior",
                                url="http://localhost:2999"
                                )

        raw_entity_wire_format_data = {'url': '/cake'}
        result = await client.reconnect_received(raw_entity_wire_format_data)
        raw_entity_wire_format_data = {'url': '/cake2'}

        # When...
        result = await client.reconnect_received(raw_entity_wire_format_data)

        # Then ... bot should now have a dungeon map created from the wire-data.
        assert_that(client._server_url).is_equal_to(
            "http://localhost:2999/cake2")
        assert_that(client._is_reconnecting).is_true()


class StopNoOpClient(EntityClient):
    async def stop_comms(self):
        """
        Over-riding this method because this bit isn't being tested here
        """
