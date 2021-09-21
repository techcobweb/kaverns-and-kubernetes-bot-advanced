import logging
import json
import asyncio.events
import socketio


from .navigation.point import Point
from .state.dungeon_map import DungeonMap
from .state.entity import Entities, Entity
from .bot import Bot
from .iclient import IEntityClient
from .state.state import State


class EntityClient(IEntityClient):
    """ Handles all the comms traffic with the outside world.
    Coordinates responses by calling other objects.
    """

    def __init__(self, character_name: str, character_role: str, url: str):
        self._character_name = character_name
        self._character_role = character_role
        self._bot: Bot = None
        self._state: State = State()
        self._server_url = url
        self._server_url_path_part = None
        self._sio = None
        self._is_reconnecting = True
        self._logger = logging.getLogger(__name__)

    def start_comms(self, async_client=None):
        while self._is_reconnecting:
            if async_client is not None:
                self._sio = async_client
            else:
                self._sio = socketio.AsyncClient(logger=False,  # Set to true to see websocket traffic
                                                 engineio_logger=False,
                                                 reconnection=True,
                                                 reconnection_attempts=10,
                                                 # How long to wait in seconds before the first
                                                 # reconnection attempt.
                                                 # Each successive attempt doubles this delay.
                                                 reconnection_delay=1,

                                                 # The maximum delay between reconnection attempts.
                                                 reconnection_delay_max=3
                                                 )
            self._sio.on('connect', self.connect_received)
            self._sio.on('connect_error', self.connect_error)
            self._sio.on('missing_role', self.missing_role_received)
            self._sio.on('map', self.map_received)
            self._sio.on('disconnect', self.disconnect_received)
            self._sio.on('entities', self.entities_received)
            self._sio.on('ping', self.ping_received)
            self._sio.on('*', self.other_event_received)
            self._sio.on('items', self.items_received)
            self._sio.on('position', self.position_received)
            self._sio.on('dead', self.dead_received)
            self._sio.on('delete', self.delete_received)
            self._sio.on('message', self.message_received)
            self._sio.on('update', self.update_received)
            self._sio.on('reconnect', self.reconnect_received)

            self._is_reconnecting = False
            self._logger.debug('asyncio-running url %s', self._server_url)
            asyncio.run(self._do_comms())
            self._logger.debug(
                'asyncio-run returned. is_reconnecting is %s', self._is_reconnecting)

    async def connect_received(self):
        self._logger.debug('> connection established')

        # The socket has a unique id (for the '/' (root) address space)
        # which we are using here for all comms.
        # That id is conveniently unique, and the server has the same
        # id on it's side, by which it knows our bot.
        # It might look something like '3r6InRBtgIE9McZNAAAn'
        my_entity_id = self._sio.get_sid()

        # We stash it away in our game state so we can look up our own
        # state in the entities list, using our own entity id.
        self._state.my_entity_id = my_entity_id

        await self._sio.emit('get_map')
        self._logger.debug("< get_map")

        # Server should respond with a 'map' command back.

        if self._bot is not None:
            self._bot.clear()

        # We won't try to reconnect, unless we get a re-connect
        # after going through a gateway.
        self._is_reconnecting = False

    async def connect_error(self, data):
        self._logger.debug("The connection failed!")
        self._logger.debug(data)

        # We won't try to reconnect, unless we get a re-connect
        # after going through a gateway.
        self._is_reconnecting = False

        return False

    async def reconnect_received(self, data):
        """
        We just walked through a gateway to a different cavern.

        ["reconnect", {url: "http://cave1-roguelike.apps.kaverns.cp.fyre.ibm.com"}]

        or it could be {url: "/path"}

        In the second case, retain the non-path part of the URL we were using previously, and 
        add the new path at the end.
        """
        self._logger.debug('> reconnect received %s', data)
        url = data.get('url')

        if url.startswith("http"):
            # It is a complete URL to go to.
            self._server_url = url
        else:
            # It is a path to use against the current URL.
            new_path_part = url

            (base_part, _) = EntityClient.split_url_parts(self._server_url)
            self._server_url = base_part + new_path_part

        self._is_reconnecting = True

        await self.stop_comms()

    @staticmethod
    def split_url_parts(url: str) -> (str, str):
        """
        Split the URL into 2 parts. The base part and the path part.

        eg: http://frontend-kandk.apps.jordan-test.cp.fyre.ibm.com/cave/0

        The base part is http://frontend-kandk.apps.jordan-test.cp.fyre.ibm.com

        The path part is /cave/0
        """
        # Find the first slash after the https:// part...
        slash_starting_path_index = url.find('/', 8)
        if slash_starting_path_index == -1:
            # There was no slash after the http:// part. So the URL has no path part.
            base_part = url
            path_part = '/'
        else:
            # Strip off the path part.
            base_part = url[0:slash_starting_path_index]
            path_part = url[slash_starting_path_index:]

        return (base_part, path_part)

    async def ping_received(self):
        await self._bot.tick()

    async def missing_role_received(self):
        self._logger.debug('> missing role !')

    async def update_received(self, data):
        self._logger.debug('> update received')
        self._logger.debug(json.dumps(data, sort_keys=False, indent=4))
        entity = Entity.from_wire_format(data)
        self._state.entities.update(entity)

    async def dead_received(self, data):
        """ The you-are-dead event sent from the server once.
        It is only sent to people who have just died.
        """
        self._logger.debug('> dead - GAME OVER')
        # Pretty Print JSON
        # self._logger.debug(json.dumps(data, sort_keys=False, indent=4))
        await self.stop_comms()

    async def delete_received(self, data):
        self._logger.debug('> deleted')

        # Pretty Print JSON
        self._logger.debug(json.dumps(data, sort_keys=False, indent=4))

        if data.get('id', None) is not None:
            # Data looks like an entity which has just died.
            # So we want to delete the entity at this point.
            wire_entity = Entity.from_wire_format(data)
            identifier = wire_entity.identifier
            self._state.entities.delete_by_id(identifier)

        else:
            # Data looks like a point, so find the entity at that point
            # and remove it.
            point = Point.from_dictionary(data)
            self._state.entities.delete_at_position(point)

    async def entities_received(self, data):
        self._logger.debug('> entities')
        # Pretty Print JSON
        # self._logger.debug(json.dumps(data, sort_keys=False, indent=4))
        self._state.entities = Entities.from_wire_format(data)

    async def map_received(self, map_data):
        self._logger.debug('> map')
        #self._logger.debug(json.dumps(map_data, sort_keys=False, indent=4))
        dungeon_map = DungeonMap.from_wire_format(map_data)
        self._state.dungeon_map = dungeon_map

    async def disconnect_received(self):
        self._logger.debug('> disconnected from server')
        return False

    async def other_event_received(self):
        self._logger.debug('> other event received.')

    async def items_received(self, data):
        """ The items detail arrives whenever it changes on this level of the dungeon,
        or when you go up/down stairs.

        It may refresh if someone else picks up an item. Not sure yet...
        """
        self._logger.debug('> items:')
        # Pretty Print JSON
        self._logger.debug(json.dumps(data, sort_keys=False, indent=4))
        self._state.update_items(data)

    async def position_received(self, data):
        self._logger.debug('> position %s', data)
        # # Pretty Print JSON
        # self._logger.debug(json.dumps(data, sort_keys=False, indent=4))
        identifier = data['id']
        point = Point.from_dictionary(data['pos'])
        self.state.update_position(identifier, point)

    async def message_received(self, message: str):
        self._logger.debug('> message:%s', message)
        self.state.messages.append(message)

    async def stop_comms(self):
        await self._sio.disconnect()

    async def _do_comms(self):
        url = self._server_url
        self._logger.debug("Connecting using %s", url)
        try:
            # Split the URL into 2 parts. The base part and the path part.
            # eg: http://frontend-kandk.apps.jordan-test.cp.fyre.ibm.com/cave/0
            # The base part is http://frontend-kandk.apps.jordan-test.cp.fyre.ibm.com
            # The path part is /cave/0
            (base_part, path_part) = EntityClient.split_url_parts(url)
            self._logger.debug(
                "Connecting to base %s path %s", base_part, path_part)

            if path_part == "/":
                await self._sio.connect(base_part,
                                        auth={'name': self._character_name,
                                              'role': self._character_role}, transports=['websocket']
                                        )
            else:
                await self._sio.connect(base_part,
                                        auth={'name': self._character_name,
                                              'role': self._character_role}, transports=['websocket'],
                                        socketio_path=path_part
                                        )

            self._logger.debug("connected ok")
            await self._sio.wait()

        except socketio.exceptions.ConnectionError as connectError:
            self._logger.error(
                "Failed to connect to server %s. %s", url, connectError)
            await self.stop_comms()

    async def send_move(self, direction):
        self._logger.debug("< send_move direction: %s", direction.name)
        await self._sio.emit('move', direction.name)

    @property
    def bot(self):
        return self._bot

    @bot.setter
    def bot(self, new_bot: Bot):
        self._bot = new_bot

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state: State):
        self._state = new_state

    async def take_item(self, item_name: str):
        self._logger.debug("< take %s", item_name)
        await self._sio.emit('take', item_name)

    async def eat_item(self, item_name: str):
        """ Tells the server to eat something from inventory """
        self._logger.debug("< eat %s", item_name)
        await self._sio.emit('eat', item_name)

    async def wear_item(self, item_name: str):
        """ Tells the server to wear something from inventory """
        self._logger.debug("< wear %s", item_name)
        await self._sio.emit('wear', item_name)

    async def wield_item(self, item_name: str):
        """ Tells the server to wield something from inventory """
        self._logger.debug("< wield %s", item_name)
        await self._sio.emit('wield', item_name)
