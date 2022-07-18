from logging import getLogger
from typing import Any, Callable, Coroutine, Optional, Protocol

from trio import run

from ..api import GatewayClient
from ..api.http import HTTPClient
from ..const import MISSING, NotNeeded
from .flags import Intents

logger = getLogger(__name__)


class BotProtocol(Protocol):
    def __init__(self, intents: Intents):
        ...

    def start(self, token: str):
        ...

    async def restart(self):
        ...

    async def on(self, coro: Coroutine, name: NotNeeded[str] = MISSING) -> Callable[..., Any]:
        ...

    @property
    def latency(self) -> float:
        ...

    @property
    def is_offline(self) -> bool:
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
    http : `HTTPClient`
        The bot's HTTP connection.
    _calls : `dict[str, list[typing.Coroutine]]`
        A set of callbacks registered by their name to their function.
        These are used to help dispatch Gateway events.
    """

    intents: Intents
    """The bot's intents."""
    _gateway: GatewayClient
    """The bot's gateway connection."""
    http: HTTPClient
    """The bot's HTTP connection."""
    _calls: dict[str, list[Coroutine]] = {}
    """
    A set of callbacks registered by their name to their function.
    These are used to help dispatch Gateway events.
    """

    def __init__(self, intents: Intents):
        self.intents = intents
        self._gateway = MISSING
        self.http = MISSING

    def start(self, token: str):
        """
        Starts a connection with Discord.

        Parameters
        ----------
        token : `str`
            The token of the bot.
        """
        self.http = HTTPClient(token)
        run(self._connect, token)

    async def restart(self):
        """Restarts a connection with Discord."""
        await self._gateway.reconnect()

    async def _connect(self, token: str):
        """
        Connects to the Gateway and hooks into the manager.

        Parameters
        ----------
        token : `str`
            The token of the bot.
        """
        async with GatewayClient(token, self.intents) as self._gateway:
            await self._gateway._hook(self)

    def _register(self, coro: Coroutine, name: Optional[str] = None, event: Optional[bool] = True):
        """
        Registers a coroutine to be used as a callback.

        Parameters
        ----------
        coro : `typing.Coroutine`
            The coroutine associated with the event.
        name : `str`, optional
            The name associated with the event. Defaults to
            the name of the coroutine, prefixed with `on_`.
        event : `bool`, optional
            Whether the coroutine is a Gateway event or not.
            Defaults to `True`.
        """
        _name = (name if event else name) if name else coro.__name__

        logger.debug(f"Registering callback for {_name}.")
        call = self._calls.get(_name, [])
        call.append(coro)

        self._calls[_name] = call

    async def _trigger(self, name: str, *args):
        """
        Triggers a name registered for callbacks.

        Parameters
        ----------
        name : `str`
            The name associated with the callbacks.
        """
        for event in self._calls.get(name, []):
            await event(*args)

    def on(
        self, coro: NotNeeded[Coroutine] = MISSING, *, name: NotNeeded[str] = MISSING
    ) -> Callable[..., Any]:
        """
        Listens to events given from the Gateway.

        ---

        `@on` is a decorator that attaches onto an asynchronous
        function or method intended to receive dispatched Gateway events.

        ---

        Example
        -------
        ```
        bot = retux.Bot(
            intents=(
                retux.Intents.GUILDS
                | retux.Intents.MESSAGE_CONTENT
            )
        )

        @bot.on
        async def on_guild_create(guild: retux.Guild):
            print(guild.member_count)

        @bot.on("message_create")
        async def message_events(message: retux.Message):
            print(message.content)
        ```

        Parameters
        ----------
        coro : `typing.Coroutine`, optional
            The coroutine to associate with the event. This is
            to be placed as a decorator on top of an asynchronous
            function.
            This is only "optional" when `name` has been specified.
        name : `str`, optional
            The name associated with the event. This defaults to the
            name of the coroutine, prefixed with `on_`.

        Returns
        -------
        `typing.Callable[..., typing.Any]`
            The coroutine associated with the event, with
            a callable pattern as to `coro`.
        """

        def decor(coro: Coroutine):
            self._register(coro, name=name if name is not MISSING else coro.__name__)
            return coro

        if coro is not MISSING:
            return decor(coro)

        return decor

    @property
    def latency(self) -> float:
        """
        The bot's latency from the Gateway.
        This is only calculated from heartbeats.
        """
        return self._gateway.latency

    @property
    def is_offline(self) -> bool:
        """
        Whether the bot is offline or not.
        May be useful for determining when to restart!
        """
        return bool(self._gateway._closed)
