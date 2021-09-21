
""" 
Processes environment variables.
"""


import os
import sys
import logging
import random


class EnvVarExtractor():
    """
    Extracts things from the environment.

    Properties:
        character_name (str) : The name of the bot
        character_role (str) : The role of the bot in the game.
        url (str) : The URL to the roguelike server
        is_ok (bool) : True if all parameters are good. False otherwise.
        speed (int): Speed of the bot. How many ticks does it ignore 
            before thinking of a move to make.
            1-10. 10 is the fastest. 1 the slowest.
            Useful if you want to follow the bot to see what it does,
            or slow it down.
            Defaults to 5, which is pretty slow.
        actions_per_turn (int):
            Each turn the bot can move along a path, how many move
            commands should it send the server at once ?
            This gives the bot warp-speed, but network vaguaries may
            cause the bot to hit walls and go in unexpected places.
            Defaults to 1.
        bot_http_server_port (int):
            The bot starts an HTTP server to indicate whether it is OK
            or not. This allows Kubernetes to monitor its' health.
            It uses this port on localhost. If None, then no HTTP 
            server will be started.
        bot_http_server_address (string):
            The http address the bot's HTTP server binds to.
            Defaults to 127.0.0.1 if not specified.
        bot_start_delay_seconds (int):
            The number of seconds delay the bot waits until it starts 
            playing. The HTTP server reports "ALIVE" until this point.
            After this point, it will report "READY".

    """

    def __init__(self, env: dict, python_version: sys.version_info) -> None:
        """Extract environment variables, and validate them.

        Parameters:
            env (dict) : A dictionary we can extract values from.
                It expects the following to be set:
                    K_AND_K_BOT_NAME
                    K_AND_K_BOT_ROLE
                    K_AND_K_SERVER_URL
                    K_AND_K_BOT_DEBUG
                    K_AND_K_BOT_SPEED
                    K_AND_K_BOT_ACTIONS_PER_TURN
                    K_AND_K_BOT_HTTP_SERVER_PORT
                    K_AND_K_BOT_HTTP_SERVER_ADDRESS
                    K_AND_K_BOT_STARTUP_DELAY_SECONDS

            python_version (sys.version_info): The version of python.
        """
        self.character_name = None
        self.character_role = None
        self.url = None
        self.is_debug = None
        self.speed = None
        self.actions_per_turn = None
        self.bot_http_server_port = None
        self.bot_http_server_address = None
        self.startup_delay_seconds = None

        self.init_startup_delay(env)
        self.init_bot_http_server_settings(env)
        self.init_debug(env)
        self.init_speed(env)
        self.init_actions_per_turn(env)

        is_ok = self.init_character_name(env)

        if is_ok:
            is_ok = self.init_character_role(env)

        if is_ok:
            is_ok = self.init_rogue_server_url(env)

        if is_ok:
            is_ok = self.check_python_pre_req_level(python_version)

        self.is_ok = is_ok

    def __str__(self):
        s = '\n'
        s += 'K_AND_K_BOT_NAME={}\n'.format(self.character_name)
        s += 'K_AND_K_BOT_ROLE={}\n'.format(self.character_role)
        s += 'K_AND_K_SERVER_URL={}\n'.format(self.url)
        s += 'K_AND_K_BOT_DEBUG={}\n'.format(self.is_debug)
        s += 'K_AND_K_BOT_SPEED={}\n'.format(self.speed)
        s += 'K_AND_K_BOT_ACTIONS_PER_TURN={}\n'.format(self.actions_per_turn)
        s += 'K_AND_K_BOT_HTTP_SERVER_PORT={}\n'.format(
            self.bot_http_server_port)
        s += 'K_AND_K_BOT_HTTP_SERVER_ADDRESS={}\n'.format(
            self.bot_http_server_address)
        s += 'K_AND_K_BOT_STARTUP_DELAY_SECONDS={}\n'.format(
            self.startup_delay_seconds)
        return s

    def check_python_pre_req_level(self, python_version: sys.version_info) -> bool:
        """ Check that the user is running the required version of python (3.8.0)
        or above.
        """
        is_ok = True
        if (python_version.major < 3) or \
                ((python_version.major == 3)
                    and (python_version.minor < 8)):
            print("Must be using python 3.8.0 or above.")
            is_ok = False
        return is_ok

    def init_actions_per_turn(self, env: dict) -> None:
        self.actions_per_turn = 1
        actions_per_turn_raw = env.get(
            'K_AND_K_BOT_ACTIONS_PER_TURN', "1")
        actions_per_turn = int(actions_per_turn_raw)
        if actions_per_turn < 1:
            print(
                "Environment variable K_AND_K_BOT_ACTIONS_PER_TURN is too small. Minumum is 1. Assumed to be 1.")
            actions_per_turn = 1
        self.actions_per_turn = actions_per_turn

    def init_speed(self, env: dict) -> None:

        self.speed = 5

        speed_raw = env.get('K_AND_K_BOT_SPEED', "5")
        speed = int(speed_raw)
        if speed < 1:
            print(
                "Environment variable K_AND_K_BOT_SPEED is too small. Range is 1-10. Assumed to be 1.")
            speed = 1
        if speed > 10:
            print(
                "Environment variable K_AND_K_BOT_SPEED is too big. Range is 1-10. Assumed to be 10.")
            speed = 10
        self.speed = speed

    def init_debug(self, env: dict) -> None:
        self.is_debug = False
        is_debug_str = env.get('K_AND_K_BOT_DEBUG', "False")
        self.is_debug = (is_debug_str == "True")

    def init_character_role(self, env: dict) -> bool:
        is_ok = True
        self.character_role = env.get('K_AND_K_BOT_ROLE', None)
        if self.character_role is None:
            print(
                "Need to specify a character role with K_AND_K_ROLE environment variable.")
            is_ok = False
        return is_ok

    def init_rogue_server_url(self, env: dict) -> bool:
        is_ok = True
        self.url: str = None

        self.url: str = env.get('K_AND_K_SERVER_URL', None)
        if self.url is None:
            print("Environment variable K_AND_K_SERVER_URL must be set.")
            is_ok = False
        elif not self.url.startswith("http://"):
            print("Environment variable K_AND_K_SERVER_URL doesn't look like a URL." +
                  " It should start with http://...")
            is_ok = False

        return is_ok

    def init_character_name(self, env: dict) -> bool:
        is_ok = True
        self.character_name = env.get('K_AND_K_BOT_NAME', None)
        if self.character_name is None:
            print(
                "Need to specify character name with K_AND_K_BOT_NAME environment variable.")
            is_ok = False
        else:
            self.character_name = self.character_name + \
                '-' + str(random.randint(0, 999))
        return is_ok

    def init_startup_delay(self, env: dict) -> None:

        raw_startup_delay_seconds = env.get(
            'K_AND_K_BOT_STARTUP_DELAY_SECONDS', None)
        if raw_startup_delay_seconds is None:
            self.startup_delay_seconds = 5
        else:
            # Max to make sure it never drops below 0
            self.startup_delay_seconds = max(int(raw_startup_delay_seconds), 0)

    def init_bot_http_server_settings(self, env: dict) -> None:
        raw_bot_http_server_port = env.get(
            'K_AND_K_BOT_HTTP_SERVER_PORT', None)
        self.bot_http_server_port = None
        if raw_bot_http_server_port is not None:
            self.bot_http_server_port = int(raw_bot_http_server_port)

        self.bot_http_server_address = env.get(
            'K_AND_K_BOT_HTTP_SERVER_ADDRESS', "127.0.0.1")
