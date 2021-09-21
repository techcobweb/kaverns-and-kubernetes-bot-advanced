"""

Interface module to declare how we use the network.

"""
from abc import ABC, abstractmethod
from .navigation.direction import Direction
from .state.state import State


class IEntityClient(ABC):
    """ An interface to a network module.
    """

    @abstractmethod
    def start_comms(self, async_client=None):
        """ starts talking to the server """

    @abstractmethod
    async def stop_comms(self):
        """ stops talking to the server """

    @abstractmethod
    async def send_move(self, direction: Direction):
        """ sends a move to the server
        Normally, this will result in the position beingg updated
        """

    @abstractmethod
    async def take_item(self, item_name: str):
        """ tells the server to take an item from the current location
        """

    @abstractmethod
    async def eat_item(self, item_name: str):
        """ Tells the server to eat something from inventory """

    @abstractmethod
    async def wear_item(self, item_name: str):
        """ Tells the server to wear something from inventory """

    @abstractmethod
    async def wield_item(self, item_name: str):
        """ Tells the server to wield something from inventory """

    @property
    def state(self) -> State:
        """ Holds the state for other parts of the system to get"""
