from typing import Protocol

from trio import run

from ..api import GatewayClient
from ..api.http import HTTPClient
from ..const import MISSING
from .flags import Intents


class BotProtocol(Protocol):
    def __init__(self, intents: Intents):
        ...

    def start(self, token: str):
        ...


class Bot(BotProtocol):
    """
    Represents a bot's connection to Discord.

    Attributes
    ----------
    intents : `Intents`
        The bot's intents.
    _gateway : `GatewayClient`
        The bot's gateway connection.
    _http : `HTTPClient`
        The bot's HTTP connection.
    """

    intents: Intents
    """The bot's intents."""
    _gateway: GatewayClient
    """The bot's gateway connection."""
    _http: HTTPClient
    """The bot's HTTP connection."""

    def __init__(self, intents: Intents):
        self.intents = intents
        self._gateway = MISSING
        self._http = MISSING

    def start(self, token: str):
        """Starts a connection with Discord."""

        # Our theory in retux here is that the token
        # will never be stored inside of the client-facing solution.
        # Only in necessary areas, such as the Gateway
        # and HTTP clients will we ever need it to run operations.

        self._gateway = GatewayClient(token, intents=self.intents)
        self._http = HTTPClient(token)

        # The nice thing here is that Trio's entry-point
        # is way more simplified.
        run(self._gateway.connect)
