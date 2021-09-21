"""This is the first piece of logic which gets executed when
python -m roguebot
is used.
"""

import os
import sys
import time
import logging
import random
from .bot import Bot
from .client import EntityClient

from .env_vars import EnvVarExtractor


def main():
    env = EnvVarExtractor(os.environ, sys.version_info)
    if env.is_ok:

        if env.is_debug:
            logging.basicConfig(level=logging.DEBUG)

        logger = logging.getLogger(__name__)
        logger.debug(str(env))

        client = EntityClient(env.character_name, env.character_role,
                              env.url)
        bot = Bot(env.character_name, client, speed=env.speed,
                  actions_per_turn=env.actions_per_turn,
                  bot_http_server_port=env.bot_http_server_port,
                  bot_http_server_address=env.bot_http_server_address,
                  startup_delay_seconds=env.startup_delay_seconds)
        client.bot = bot

        # Run the game on this thread. This blocks until the bot dies.
        bot.play()


if __name__ == '__main__':
    main()
