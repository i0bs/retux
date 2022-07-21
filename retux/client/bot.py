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

    def close(self):
        ...

    async def restart(self):
        ...

    async def on(self, coro: Coroutine, name: NotNeeded[str] = MISSING) -> Callable[..., Any]:
        ...

    @property
    def latency(self) -> float:
        ...

    @property
    def offline(self) -> bool:
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

    def close(self):
        """Closes the current connection with Discord."""
        self._gateway._stopped = True

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

        Examples
        --------
        In retux, `event` is an argument containing the information relating
        to the event you're listening to. This argument is always required
        for an `@on` coroutine. `event` can be anything so as long as it's
        dispatched and subclassed as a `_Event`. In any case, however, you
        can always typehint it as what the event is intending to listen to.
        ```
        @bot.on
        async def ready(event):
            print(f"Hello, world! I am {event.user.username}. Running on API version v{event.version}.")
        ```

        If you'd like to still take control of the coroutine's name,
        however, you can simply pass the event name into the `@on`
        decorator.
        ```
        @bot.on("ready")
        async def func_name(event):
            ...
        ```

        `@on` empowers developers to also determine when a restart may
        be needed without having to create your own loop. Please note
        that this is only an example. retux automatically attempts reconnections
        if one is called for, including invalidated sessions.
        ```
        @bot.on
        async def reconnect(event: typing.Any):
            if bot.is_offline:
                await bot.restart()
        ```

        Sometimes, however, you may want to provide something a little bit
        more structural and organised than numerous functions laid out all
        over the place. Instead of resorting these into an extension,
        we have created what's known as "event classes" for this instead.
        ```py
        @bot.on
        class MessageEvent:
            async def create(message: retux.Message):
                ...
            async def remove(message, before, after):
                ...
        ```

        The nicest part of this is that you can create your own event handlers
        for attributes changing, done with `async def channel_id(value)`!

        Additionally, you can also provide converters for your message event,
        in case you do not feel like specifying it via. `create` and etc., such
        as `async def to_voice(channel: retux.VoiceChannel)`.

        If a bot developer so wishes to create their own functions inside of
        the class as well, it is highly recommended to dunder (add an `_` to
        the beginning of) their custom-defined methods. This poses no issue
        to retux's handling, but helps you as the bot developer keep up with
        what you're doing.

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
    def offline(self) -> bool:
        """
        Whether the bot is offline or not.
        May be useful for determining when to restart!
        """
        return bool(self._gateway._closed)
