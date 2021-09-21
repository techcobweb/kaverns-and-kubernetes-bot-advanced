import json
import unittest
import requests
import logging
from assertpy import assert_that
from unittest.mock import Mock
from roguebot.bot import Bot
from roguebot.httpserver.bot_http_server import BotHttpServer


logging.basicConfig(level=logging.DEBUG)


def test_can_create_an_http_server_object_with_defaults() -> None:
    server = BotHttpServer()
    assert_that(server._port).is_equal_to(9088)
    assert_that(server._address).is_equal_to("127.0.0.1")


def test_can_start_server_get_status_stop_server() -> None:
    server = BotHttpServer(port=4000)
    server.start()
    server.stop()


class HttpServerUrlTest(unittest.TestCase):

    bot: Bot = None
    port: int = 4005
    server: BotHttpServer = None

    @classmethod
    def setUpClass(cls):
        """
        Sets up an HTTP server.
        """
        HttpServerUrlTest.bot = Mock(spec=Bot)
        HttpServerUrlTest.port = 4005
        HttpServerUrlTest.server = BotHttpServer(
            bot=HttpServerUrlTest.bot, port=HttpServerUrlTest.port)
        HttpServerUrlTest.server.start()

    @classmethod
    def tearDownClass(cls):
        """
        Closes down the HTTP server
        """
        HttpServerUrlTest.server.stop()

    def test_can_get_404_if_url_is_bad(self) -> None:
        HttpServerUrlTest.bot.got_enough_state_to_start.return_value = True
        HttpServerUrlTest.bot.status_summary = {}
        url = "http://localhost:{}/unknown".format(HttpServerUrlTest.port)

        response = requests.get(url)

        status_code = response.status_code
        assert_that(status_code).is_equal_to(404)

    def test_can_get_complex_status_when_ready(self) -> None:
        HttpServerUrlTest.bot.got_enough_state_to_start.return_value = True
        HttpServerUrlTest.bot.status_summary = {}
        url = "http://localhost:{}/status".format(HttpServerUrlTest.port)

        response = requests.get(url)

        response_dict = response.json()
        status = response_dict.get("status", None)
        assert_that(status).is_equal_to("READY")

    def test_can_get_complex_status_when_not_ready(self) -> None:
        HttpServerUrlTest.bot.got_enough_state_to_start.return_value = False
        url = "http://localhost:{}/status".format(HttpServerUrlTest.port)

        response = requests.get(url)

        response_dict = response.json()
        status = response_dict.get("status", None)
        assert_that(status).is_equal_to("ALIVE")

    def test_can_get_simple_status_when_ready(self) -> None:
        HttpServerUrlTest.bot.got_enough_state_to_start.return_value = True
        url = "http://localhost:{}/".format(HttpServerUrlTest.port)

        response = requests.get(url)

        response_dict = response.json()
        status = response_dict.get("status", None)
        assert_that(status).is_equal_to("READY")

    def test_can_get_simple_status_when_not_ready_yet(self) -> None:
        HttpServerUrlTest.bot.got_enough_state_to_start.return_value = False
        url = "http://localhost:{}/".format(HttpServerUrlTest.port)

        response = requests.get(url)

        response_dict = response.json()
        status = response_dict.get("status", None)
        assert_that(status).is_equal_to("ALIVE")

    def test_can_give_up_if_http_server_doesnt_respond(self) -> None:
        HttpServerUrlTest.server._port = 4007  # Wrong port

        is_ok = HttpServerUrlTest.server._wait_until_server_starts_replying_to_traffic()

        assert_that(is_ok).is_false()

    def test_can_get_ready_url_when_not_ready_yet_gives_503_error(self) -> None:
        HttpServerUrlTest.bot.got_enough_state_to_start.return_value = False
        url = "http://localhost:{}/ready".format(HttpServerUrlTest.port)

        response = requests.get(url)

        assert_that(response.status_code).is_equal_to(503)

    def test_can_get_ready_url_when_ready_gives_200_ok(self) -> None:
        HttpServerUrlTest.bot.got_enough_state_to_start.return_value = True
        url = "http://localhost:{}/ready".format(HttpServerUrlTest.port)

        response = requests.get(url)

        assert_that(response.status_code).is_equal_to(200)
