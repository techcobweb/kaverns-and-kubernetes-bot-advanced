"""
Represents the 'bot' playing the game using the entity client.
"""

import logging
import time

from .iclient import IEntityClient
from .brains.brain import GoalDrivenBrain
from .brains.megabrain import MegaBrain
from .brains.item_handling_brain import ItemHandlingBrain
from .brains.ibrain import IBrain
from .httpserver.bot_http_server import BotHttpServer


class Bot():
    """
    Represents the 'bot' playing the game using the entity client.

    Separated from the state of the world. That's in the 'state' object.

    Parameters:
        character_name (str): The name of the bot.
        client (IEntityClient): The client, dealing with network traffic.
        brain_name (str): Where multiple brains are supported, which one
            do we use ? eg: GoalDrivenBrain
        speed (int) : Number from 1-10 inclusive. 10 is faster.
            Controls how many 'turns' we ignore before making a move.
            Defaults to 5.
        actions_per_turn (int) : Number of actions we try to mave in one
            turn. Larger numbers may hit a server limit.
            Defaults to 1
        startup_delay_seconds (int) : Number of seconds to wait between
            the 'ALIVE' state, and the 'READY' state.
    """

    def __init__(self,
                 character_name: str,
                 client: IEntityClient,
                 brain_name="MegaBrain",
                 speed: int = 5,
                 actions_per_turn: int = 1,
                 bot_http_server_port: int = None,
                 bot_http_server_address: str = "127.0.0.1",
                 startup_delay_seconds=0
                 ):
        self._logger = logging.getLogger(__name__)

        self._character_name = character_name

        self._tick_count = 0

        self._logger.debug("Speed is %s", speed)
        self._ignore_ticks_before_act = 11-speed
        self._logger.debug("Going to act once every %s ticks",
                           self._ignore_ticks_before_act)

        self._client = client
        self._brain = self._select_brain(brain_name)

        # Tell the brain how many actions we want maximum per turn.
        self._brain.max_actions_per_turn = actions_per_turn

        # game events from the network are sent to the entity client.
        # tell the entity client about ourselves so it can call us back
        # when certain events occur. eg:when the timer ticks.
        client.bot = self

        self._bot_http_server_port = bot_http_server_port
        self._bot_http_server_address = bot_http_server_address
        self._startup_delay_seconds = startup_delay_seconds

    def _select_brain(self, brain_name: str) -> IBrain:
        """ Dynamicall loads a brain based on it's name.
        Though we must have them all imported into the global namespace.
        """
        self._logger.debug("Loading brain %s", brain_name)

        def get_class(class_name):
            return globals()[class_name]
        class_code = get_class(brain_name)
        instance = class_code()

        return instance

    @property
    def state(self):
        """
        Returns:
            state (State): The state of the world.
        """
        return self._client.state

    @state.setter
    def state(self, new_state):
        """
        Sets a new state of the world for the bot to remember.

        Parameters:
            new_state (State): The new state of the world to use.
        """
        self._client.state = new_state

    def clear(self):
        """
        We have entered a new cave, either the first cave,
        or another one after going through a gateway.

        So clear-out any state we might have in the brain,
        as they are not relevent any longer.
        """
        if self._brain is not None:
            self._brain.clear()

    def play(self):
        """ Starts the bot playing a game.

        This call blocks until the bot is dead.
        """
        http_server = None

        # Start up the health server... if the port is set.
        if self._bot_http_server_port is not None:
            http_server = BotHttpServer(self._bot_http_server_address,
                                        self._bot_http_server_port,
                                        self)
            http_server.start()

        if self._startup_delay_seconds > 0:
            self._logger.debug(
                "Waiting for a bit before we start playing (%s seconds)",
                self._startup_delay_seconds)
            time.sleep(self._startup_delay_seconds)
            self._logger.debug("Wait is over. Lets play...")

        self._client.start_comms()

        if self._bot_http_server_port is not None:
            # Stop the server on our 2nd thread..
            http_server.stop()

    def got_enough_state_to_start(self) -> bool:
        """ Have we got enough state to start processing using a brain ? 
        """
        state = self.state
        if state is None:
            self._logger.debug(
                "Not got enough state to start yet... waiting... no state.")
        elif state.dungeon_map is None:
            self._logger.debug(
                "Not got enough state to start yet... waiting... no map.")
        elif state.my_entity_id is None:
            self._logger.debug(
                "Not got enough state to start yet... waiting... no id for myself.")
        elif state.entities.get_by_id(state.my_entity_id) is None:
            self._logger.debug(
                "Not got enough state to start yet... waiting... my entity not found in entities list")
        else:
            return True

        return False

    @property
    def status_summary(self) -> dict:
        """
        A summary of the bot status, housed in a dict object.
        """
        summary = {}
        if self._brain is not None:
            summary = self._brain.status_summary
        return summary

    async def tick(self):
        """
        A regular clock 'tick' so we can do something whenever this happens.
        """

        if self.got_enough_state_to_start():
            # Only do anything every n ticks... to slow things down.
            if self._tick_count >= self._ignore_ticks_before_act:
                self._tick_count = 0
                await self._do_action()
            self._tick_count += 1

    async def _do_action(self):
        """
        Do something amazing ! 
        """
        # print("> do_action")

        # Find out which actions the brain thinks we should be doing.
        actions = self._brain.decide_actions(self.state)

        self._logger.debug("actions: %s", actions)

        # Enact those actions
        for action in actions:

            # Tell the server to do something through the client.
            await action.do_action(self._client)
