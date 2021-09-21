"""
All things to do with actions which the brain can generate, for the bot's body to perform.
"""

from abc import ABC, abstractmethod
from enum import Enum
from .navigation.direction import Direction
from .iclient import IEntityClient


class ActionCode(Enum):
    """
    Each action has a code, so we can easily tell which type of action it is
    without having to check the instance further.
    """
    MOVE = 1
    TAKE = 2
    EAT = 3
    WEAR = 4
    WIELD = 5


class Action(ABC):
    """
    An action that a brain will decide to perform.

    The brain is asked "what do you want to do?" and it replies "these actions"

    There are several types of action inheriting from the base Action class.

    Each action has a distinct ActionCode value unique to that subclass, so
    code can easily know (and test) which action is wanted.

    This class allows us to separate what the brain wants, from the act
    of doing what is desired. Useful in unit testing when we want to
    test the brain, but not send commands to the server over the network.
    """

    def __init__(self, action_code: ActionCode):
        self._action_code = action_code

    def __repr__(self):
        """ If there is a list of objects, and someone prints the list,
        it would normally output some object reference hex number.
        """
        return str(self)

    @property
    def action_code(self):
        """
        Provides easy programmatic access to which type of action this is.
        """
        return self._action_code

    @abstractmethod
    async def do_action(self, client: IEntityClient):
        """ Every sub-class of action implements their own version of this method.
        Each action will be different, and will do a different thing.
        """


class MoveAction(Action):
    """
    An action which will try to move the bot around.
    """

    def __init__(self, direction: Direction):
        super().__init__(ActionCode.MOVE)
        self._direction = direction

    def __str__(self):
        return "MoveAction. {}".format(self._direction.name)

    @property
    def direction(self):
        """ The direction we want to move in for this action. """
        return self._direction

    async def do_action(self, client: IEntityClient):
        """
        Called by the bot to enact the action onto the client and network.
        Allows each action to keep everything together, so the bot
        doesn't have to understand what to do for each action.
        """
        await client.send_move(self._direction)


class ItemAction(Action):
    """
    An abstract notion of an action which does something to an item.
    """

    def __init__(self, action_code: ActionCode, item_name: str):
        super().__init__(action_code)
        self._item_name = item_name

    @property
    def item_name(self):
        """ The name of the item acted upon """
        return self._item_name

    def __str__(self):
        return super().__str__() + " " + self._item_name


class TakeAction(ItemAction):
    """
    When we want to take or pick something up.
    """

    def __init__(self, item_name: str):
        """ When we want to take or pick something up """
        super().__init__(ActionCode.TAKE, item_name)

    def __str__(self):
        return "TakeAction. {}".format(self._item_name)

    async def do_action(self, client: IEntityClient):
        await client.take_item(super().item_name)


class EatAction(ItemAction):
    """
    Eat an item that is already in the inventory.
    """

    def __init__(self, item_name: str):
        """ When we want to eat something from our inventory """
        super().__init__(ActionCode.EAT, item_name)

    def __str__(self):
        return "EatAction. {}".format(self._item_name)

    async def do_action(self, client: IEntityClient):
        await client.eat_item(self._item_name)


class WearAction(ItemAction):
    """
    Wear an item that is already in the inventory
    """

    def __init__(self, item_name: str):
        """ When we want to wear something from our inventory """
        super().__init__(ActionCode.WEAR, item_name)

    def __str__(self):
        return "WearAction. {}".format(self._item_name)

    async def do_action(self, client: IEntityClient):
        await client.wear_item(self._item_name)


class WieldAction(ItemAction):
    """
    Wield a weapon to do damage.
    """

    def __init__(self, item_name: str):
        """ When we want to wield something from our inventory as a weapon"""
        super().__init__(ActionCode.WIELD, item_name)

    def __str__(self):
        return "WieldAction. {}".format(self._item_name)

    async def do_action(self, client: IEntityClient):
        """
        Tell the client to do whatever you need to achieve this action.
        """
        await client.wield_item(self._item_name)
