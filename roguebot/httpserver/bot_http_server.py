"""
A simple HTTP server which responds to GET requests to see if the bot is up and running or not

Kubernetes uses this to assess whether the bot needs to be re-started or not.

"""
import logging
import threading
import time
import json
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from ..state.state import State


class BotHttpServer():
    """
    An HTTP server, so Kubernetes can ask "are you ok?" 
    and we can say "OK"

    It gets started when the bot starts, and
    when the bot dies it gets closed.

    Paths supported are:
        /       : Gives the status.
        /status : Gives the status.

    """

    def __init__(self, address: str = "127.0.0.1", port: int = 9088, bot=None):
        """
        Sets up the simple HTTP server
        """
        self._server_thread = None
        self._port = port
        self._logger = logging.getLogger(__name__)
        self._http_server = None
        self._bot = bot
        self._address = address

    def start(self) -> bool:
        """
        Start the HTTP server
        """
        self._server_thread = threading.Thread(
            target=self.thread_function, args=(1,))
        self._server_thread.start()
        is_http_server_working = self._wait_until_server_starts_replying_to_traffic()
        return is_http_server_working

    def _wait_until_server_starts_replying_to_traffic(self) -> bool:
        """
        Send GET requests to the HTTP server until it starts
        replying OK.

        Returns:
            is_http_server_working (bool): True if the server is working,
                false if we gave up waiting.
        """
        self._logger.debug("waiting for server to start up")
        url = "http://localhost:{}/".format(self._port)
        is_http_server_working = False
        attempt_count = 0
        while attempt_count < 10 and not is_http_server_working:
            attempt_count += 1

            self._logger.debug(
                "Checking URL %s", url)
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    is_http_server_working = True
                    self._logger.debug("Http server is ready now")
            except requests.ConnectionError as ex:
                # Ignore the exception and re-try
                self._logger.debug(
                    "Http server is having problems. %s", ex)

                time.sleep(0.1)  #  Seconds

        return is_http_server_working

    def stop(self):
        """
        Stop the HTTP server.
        """
        self._logger.debug("About to stop the http server")

        self._http_server.shutdown()

        # Wait for the server thread to stop.
        self._logger.debug("Waiting for the http server to stop")
        self._server_thread.join()

    def thread_function(self, thread_name: str):
        """
        This thread runs the HTTP server, so the main thread
        can continue playing the game.
        """
        self._logger.debug("Thread %s: starting", thread_name)

        # Start our http server in this thread.
        server_address = (self._address, self._port)
        self._logger.debug("Serving from address %s", server_address)
        self._http_server = StoppableHTTPServer(
            server_address, HTTPRequestHandler, self._bot)
        self._logger.debug("Server %s", self._http_server)
        self._http_server.run()
        self._logger.debug("Thread %s: finishing", thread_name)


class StoppableHTTPServer(HTTPServer):
    """
    An HTTP server which can be stopped programmatically.
    """

    def __init__(self, address, handler_class, bot=None):
        super().__init__(address, handler_class)
        self._bot = bot

    @property
    def bot(self):
        return self._bot

    def run(self):
        """
        Runs the server, fielding HTTP requests, until a
        different thread calls the 'shudown()' method.
        """
        try:
            self.serve_forever()
        # except KeyboardInterrupt:
        #     pass
        finally:
            # Clean-up server (close socket, etc.)
            self.server_close()


class HTTPRequestHandler(BaseHTTPRequestHandler):
    """
    Processes HTTP requests
    """

    def __init__(self, request, client_addr, server):
        logging.basicConfig(level=logging.DEBUG)
        self._logger = logging.getLogger(__name__)
        super().__init__(request, client_addr, server)

    def do_GET(self):
        """
        Respond to a GET request.
        """
        bot = self.server.bot

        is_ready = False

        if bot is not None:
            is_ready = self.server.bot.got_enough_state_to_start()

        if self.path == "/":
            self._complete_request(self._get_simple_status(is_ready))

        elif self.path == "/ready":
            content = self._get_simple_status(is_ready)
            if is_ready:
                self._complete_request(content)
            else:
                self._complete_request(content, http_code=503)

        elif self.path == "/status":
            content = self._get_simple_status(is_ready)
            if is_ready:
                bot_status = self.server.bot.status_summary
                # Merge the two dictionaries into one.
                content = {**content, **bot_status}
            self._complete_request(content)
        else:
            self.send_error(404)

    def _get_simple_status(self, is_ready: bool) -> dict:
        """
        Returns:
            simple_status (dict): a dictionary containing {"status":"Alive"}
                or {"status":"Ready"}, depending on whether the bot thinks
                there is enough state to be playing (ready) or not (alive).
        """
        if is_ready:
            status = 'READY'
        else:
            status = 'ALIVE'
        simple_status = {
            "status": status
        }
        return simple_status

    def _complete_request(self, content: dict = None, http_code=200) -> None:
        """
        Use the content provided to form a response to some request we are processing,
        and send the response back.

        Parameters:
            content (dict) : The json content we will send back in the response body.
        """
        json_content_string = json.dumps(content)
        formatted_content = bytes(json_content_string, 'utf-8')
        self._logger.debug("do_GET: sending back %s", formatted_content)
        self.send_response(http_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(formatted_content)
