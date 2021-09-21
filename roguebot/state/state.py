"""
State of the world is stored here.

Note: 
    The `Client` updates the state when told to by the server.
    
    The `Brain` and `Goal` logic examines the state in order to decide what to do next.
"""
import json
import logging

from ..navigation.point import Point
from .entity import Entities, Entity
from .item import Items
from .dungeon_map import DungeonMap


class State():
    """
    The state of the world.
    """

    def __init__(self,
                 name: str = None,
                 dungeon_map: DungeonMap = None,
                 entities: Entities = None,
                 items: Items = None,
                 my_entity_id: str = None):
        """
        Construct a state.

        Parameters:
            name (str): Optional. The name of the character bot.
                Or None by default.
            dungeon_map (DungeonMap) : Optional. The map of the entire dungeon.
                If it is known, or None if it will be set later.
            entities (Entities): Optional. The entities in the state, if known.
                or an empty Entities object if not specified or None.
            items (Items): Optional. The items in the state, if known,
                or an empty Items object if not specified or None.
            my_identity_id (str): The unique identity of the bot's own entity,
                which also should appear in the Entities object collection.

        """
        self._character_name = name
        self._dungeon_map = dungeon_map
        if entities is None:
            self._entities = Entities()
        else:
            self._entities = entities

        if items is None:
            self._items = Items()
        else:
            self._items = items

        self._my_entity_id = my_entity_id
        self._messages = list()
        self._logger = logging.getLogger(__name__)

    def find_my_entity(self) -> Entity:
        """
        Use the my_entity_id property within the state to find the
        entity representing the bot in the available entities.
        """
        me = self._entities.get_by_id(self._my_entity_id)
        return me

    @property
    def messages(self):
        return self._messages

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, new_items):
        self._items = new_items

    @property
    def my_entity_id(self):
        """A unique id by which the server knows this bot.

        We get it from the 'sid' of the web socket, for the default
        namespace.

        It might look something like '3r6InRBtgIE9McZNAAAn'
        and we can look up our own state from the entities list
        using this.
        """
        return self._my_entity_id

    @my_entity_id.setter
    def my_entity_id(self, entity_id):
        """
        The network layer sets our entity id here as soon as the
        connection is established.
        """
        self._logger.debug("My entity id is now set to %s", entity_id)
        self._my_entity_id = entity_id

    @property
    def dungeon_map(self):
        return self._dungeon_map

    @dungeon_map.setter
    def dungeon_map(self, new_map):
        self._dungeon_map = new_map

    @property
    def entities(self):
        return self._entities

    @entities.setter
    def entities(self, entities):
        self._entities = entities

    def update_items(self, items_data):
        """
        Information about items has just arrived
        """
        # Find myself in the list of entities.
        # As we want to delete every item from our current dungeon level
        # and have them replaced.
        me = self.find_my_entity()
        self._items.update_items(items_data, me.position)

    def update_position(self, identifier: str, position: Point):
        """
        Updates the position of the entity who's id is specifed.
        """
        self._entities.update_position(identifier, position)
