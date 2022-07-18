from enum import IntEnum
from json import dumps, loads
from logging import getLogger
from sys import platform
from time import perf_counter
from typing import Any, Protocol

from attrs import asdict, define, field
from cattrs import structure_attrs_fromdict
from trio import open_nursery, sleep, Nursery
from trio_websocket import ConnectionClosed, WebSocketConnection, open_websocket_url

from .factories.factory import Factory

from ..client.flags import Intents
from ..client.resources.abc import Snowflake
from ..const import MISSING, NotNeeded, __gateway_url__

logger = getLogger(__name__)


@define()
class _GatewayMeta:
    """Represents metadata for a Gateway connection."""

    version: int = field()
    """The version of the Gateway."""
    encoding: str = field()
    """The encoding type on Gateway payloads."""
    compress: str | None = field(default=None)
    """The compression type on Gateway payloads."""
    heartbeat_interval: float | None = field(default=None)
    """The heartbeat used to keep a Gateway connection alive."""
    session_id: str | None = field(default=None)
    """The ID of an existent session, used for when resuming a lost connection."""
    seq: int | None = field(default=None)
    """The sequence number on an existent session."""


class _GatewayOpCode(IntEnum):
    """Represents a Gateway event's operation code."""

    DISPATCH = 0
    """An event has been received."""
    HEARTBEAT = 1
    """A handshake sent periodically to ensure an alive connection."""
    IDENTIFY = 2
    """An identification event to start a session with the initial handshake."""
    PRESENCE_UPDATE = 3
    """An event sent to update the client's presence."""
    VOICE_STATE_UPDATE = 4
    """An event sent to update the client's voice state."""
    RESUME = 6
    """An event sent to resume a previous connection prior to disconnect."""
    RECONNECT = 7
    """An event received informing the client to reconnect."""
    REQUEST_GUILD_MEMBERS = 8
    """An event sent to receive information on offline guild members."""
    INVALID_SESSION = 9
    """
    An event received informing the client the connection has been invalidated.
    `RECONNECT` ultimately follows this.
    """
    HELLO = 10
    """An event received on a successfully initiated connection."""
    HEARTBEAT_ACK = 11
    """An event received to acknowledge a `HEARTBEAT` sent."""


@define(slots=False)
class _GatewayPayload:
    """
    Represents a Gateway payload, signifying data for events.

    The `s` (`sequence`) and `t` (`name`) attributes will only have
    a value when:

    - `op` (`opcode`) is `DISPATCH`.
    - A `RESUME` call has been made. (specific to the former)
    """

    op: int | _GatewayOpCode = field(converter=int)
    """The opcode of the payload."""
    d: Any | None = field(default=None)
    """The payload's event data."""
    s: int | None = field(default=None)
    """The sequence number, used for resuming sessions and heartbeats."""
    t: str | None = field(default=None)
    """The name of the payload's event."""

    @property
    def opcode(self) -> int:
        """The opcode of the payload."""
        return self.op

    @property
    def data(self) -> Any | None:
        """The payload's event data"""
        return self.d

    @property
    def sequence(self) -> int | None:
        """The sequence number, used for resuming sessions and heartbeats."""
        return self.s

    @property
    def name(self) -> str | None:
        """The name of the payload's event."""
        return self.t


class GatewayProtocol(Protocol):
    def __init__(
        self,
        token: str,
        intents: Intents,
        *,
        version: int = 10,
        encoding: str = "json",
        compress: NotNeeded[str] = MISSING,
    ):
        ...

    async def connect(self):
        ...

    async def reconnect(self):
        ...

    async def request_guild_members(
        self,
        guild_id: Snowflake,
        *,
        query: NotNeeded[str] = MISSING,
        limit: NotNeeded[int] = MISSING,
        presences: NotNeeded[bool] = MISSING,
        user_ids: NotNeeded[Snowflake | list[Snowflake]] = MISSING,
        nonce: NotNeeded[str] = MISSING,
    ):
        ...

    async def update_voice_state(
        self,
        guild_id: Snowflake,
        channel_id: NotNeeded[Snowflake] = MISSING,
        self_mute: NotNeeded[bool] = MISSING,
        self_deaf: NotNeeded[bool] = MISSING,
    ):
        ...

    @property
    def latency(self) -> float:
        ...


class GatewayClient(GatewayProtocol):
    """
    Represents a connection to Discord's Gateway. Gateways are Discord's
    form of real-time communication over secure WebSockets. Clients will
    receive events and data over the Gateway they are connected to and
    send data over the REST API.

    Upon instantiation, the class will attempt to assign encoding
    and compression values. Please see the documentation when instantiating
    for more details.

    ---

    Attributes
    ----------
    token : `str`
        The bot's token.
    intents : `Intents`
        The intents to connect with.
    _conn : `trio_websocket.WebSocketConnection`
        An instance of a connection to the Gateway.
    _meta : `_GatewayMeta`
        Metadata representing connection parameters for the Gateway.
    _tasks : `trio.Nursery`
        The tasks associated with the Gateway, for reconnection and heartbeating.
    _closed : `bool`
        Whether the Gateway connection is closed or not.
    _heartbeat_ack : `bool`
        Whether we've received the first heartbeat acknowledgement or not.
    _last_ack : `list[float]`
        The before/after time of the last Gateway event tracked. See `latency` for Gateway connection timing.
    _bots : `list[retux.Bot]`
        The bot instances used for dispatching events.
    """

    # TODO: Add sharding and presence changing.

    __slots__ = ("token", "intents", "_meta")
    token: str
    """The bot's token."""
    intents: Intents
    """The intents to connect with."""
    _conn: WebSocketConnection = None
    """An instance of a connection to the Gateway."""
    _meta: _GatewayMeta
    """Metadata representing connection parameters for the Gateway."""
    _tasks: Nursery = None
    """The tasks associated with the Gateway, for reconnection and heartbeating."""
    _closed: bool = True
    """Whether the Gateway connection is closed or not."""
    _heartbeat_ack: bool = False
    """Whether we've received the first heartbeat acknowledgement or not."""
    _last_ack: list[float] = []
    """The before/after time of the last Gateway event tracked. See `latency` for Gateway connection timing."""
    _bots: list["Bot"] = []  # noqa
    """The bot instances used for dispatching events."""

    def __init__(
        self,
        token: str,
        intents: Intents,
        *,
        version: int = 10,
        encoding: str = "json",
        compress: str = None,
    ):
        """
        Creates a new connection to the Gateway.

        Parameters
        ----------
        token : `str`
            The bot's token to connect with.
        intents : `Intents`
            The intents to connect with.
        version : `int`, optional
            The version of the Gateway to use. Defaults to version `10`.
        encoding : `str`, optional
            The type of encoding to use on payloads. Defaults to `json`.
        compress : `str`, optional
            The type of data compression to use on payloads. Defaults to none.
        """
        self.token = token
        self.intents = intents
        self._meta = _GatewayMeta(version=version, encoding=encoding, compress=compress)

    async def __aenter__(self):
        self._tasks = open_nursery()
        nursery = await self._tasks.__aenter__()
        nursery.start_soon(self.reconnect)
        nursery.start_soon(self._heartbeat)
        return self

    async def __aexit__(self, *exc):
        return await self._tasks.__aexit__(*exc)

    async def _receive(self) -> _GatewayPayload:
        """
        Receives the next incoming payload from the Gateway.

        Returns
        -------
        `_GatewayPayload`
            A class of the payload data.
        """

        # FIXME: our exception handling neglects other rejection
        # reasons. A more thorough analysis of trio_websocket
        # is necessary to have an extensible exception of our
        # own for clarifying connection loss.

        try:
            resp = await self._conn.get_message()
            json = loads(resp)
            return structure_attrs_fromdict(json, _GatewayPayload)
        except ConnectionClosed:
            logger.warn("The connection to Discord's Gateway has closed.")
            self._closed = True
            await self.reconnect()

    async def _send(self, payload: _GatewayPayload):
        """
        Sends a payload to the Gateway.

        Parameters
        ----------
        payload : `_GatewayPayload`
            The payload to send.
        """

        try:
            json = dumps(asdict(payload))
            resp = await self._conn.send_message(json)  # noqa
        except ConnectionClosed:
            logger.warn("The connection to Discord's Gateway has closed.")
            await self._conn.aclose()
            await self.reconnect()

    async def connect(self):
        """Connects to the Gateway and initiates a WebSocket state."""
        self._last_ack = [perf_counter(), perf_counter()]

        # FIXME: this connection type will only work with JSON in mind.
        # if other compression or encoding types are supplied, they
        # will not be properly digested. This is only added so others
        # may modify their GatewayClient to their liking.

        async with open_websocket_url(
            f"{__gateway_url__}?v={self._meta.version}&encoding={self._meta.encoding}"
            f"{'' if self._meta.compress is None else f'&compress={self._meta.compress}'}"
        ) as self._conn:
            self._closed = self._conn.closed

            if self._closed:
                await self._conn.aclose()
                await self.reconnect()

            while not self._closed:
                data = await self._receive()

                if data:
                    await self._track(data)

    async def reconnect(self):
        """Reconnects to the Gateway and reinitiates a WebSocket state."""
        self._closed = True
        self._heartbeat_ack = False

        if self._closed:
            await self.connect()
        else:
            logger.info("Told to reconnect, but did not need to.")

    async def _track(self, payload: _GatewayPayload):
        """
        Tracks data sent from the Gateway and interprets it.

        Parameters
        ----------
        payload : `_GatewayPayload`
            The payload being sent from the Gateway.
        """
        logger.debug(
            f"Tracking payload: {payload.opcode}{'.' if payload.name is None else f' ({payload.name})'}"
        )

        match _GatewayOpCode(payload.opcode):
            case _GatewayOpCode.HELLO:
                if self._meta.session_id:
                    logger.debug("Prior connection found, trying to resume.")
                    await self._resume()
                else:
                    logger.debug("New connection found, identifying to the Gateway.")
                    await self._identify()
                    self._meta.heartbeat_interval = payload.data["heartbeat_interval"] / 1000
                    logger.debug(f"Heartbeat set to {self._meta.heartbeat_interval}ms.")
                    self._heartbeat_ack = True
                    logger.debug("Began the heartbeat process.")
            case _GatewayOpCode.HEARTBEAT_ACK:
                self._last_ack[1] = perf_counter()
                logger.debug(f"The heartbeat was acknowledged. (took {self.latency}ms.)")
                self._last_ack[0] = perf_counter()
            case _GatewayOpCode.INVALID_SESSION:
                logger.info(
                    "Our Gateway connection has suddenly invalidated. Starting new connection."
                )
                self._meta.session_id = None
                await self._conn.aclose()
                await self.reconnect()
            case _GatewayOpCode.RECONNECT:
                logger.info("The Gateway has told us to reconnect.")
                if payload.data:
                    logger.info("Resuming last known connection.")
                    await self._resume()
                else:
                    await self._conn.aclose()
                    await self.reconnect()
            case _GatewayOpCode.DISPATCH:
                logger.debug(f"Dispatching {payload.name}")
                await self._dispatch(payload.name, payload.data)
        match payload.name:
            case "RESUMED":
                logger.debug(
                    f"The connection was resumed. (session: {self._meta.session_id}, sequence: {self._meta.seq}"
                )
            case "READY":
                self._meta.session_id = payload.data["session_id"]
                self._meta.seq = payload.sequence
                logger.debug(
                    f"The Gateway has declared a ready connection. (session: {self._meta.session_id}, sequence: {self._meta.seq}"
                )

    async def _hook(self, bot: "Bot"):  # noqa
        """
        Hooks the Gateway to a bot for event dispatching.

        ---

        The `bot` field allows for numerous bots in theory
        to be hooked onto with one `GatewayClient` process
        being ran, allowing for IPC pipes and more intuitive
        sharding.

        ---

        Parameters
        ----------
        bot : `retux.Bot`
            The bot instance to hook onto. This instance
            can be any bot instance for interchangable
            handling of 1 main Gateway.
        """
        logger.debug("Hooking the bot into the Gateway.")
        self._bots.append(bot)

    async def _dispatch(self, name: str, data: dict):
        """
        Dispatches an event from the Gateway.

        ---

        "Dispatching" is when the Gateway sends the client
        information regarding an event non-relevant to
        the connection.

        ---

        Parameters
        ----------
        name : `str`
            The name of the event.
        data : `dict`
            The supplied payload data from the event.
        """
        try:
            resource = Factory.define(name, data)
        except AttributeError:
            resource = MISSING
            logger.info(f"The Gateway sent us {name} with no data class found.")

        for bot in self._bots:
            await bot._trigger(name.lower(), resource)

        # TODO: implement the gateway rate limiting logic here.
        # the theory of this is to "queue" dispatched informatoin
        # from the Gateway when we enter a rate limit.

    async def _identify(self):
        """Sends an identification payload to the Gateway."""
        payload = _GatewayPayload(
            op=_GatewayOpCode.IDENTIFY.value,
            d={
                "token": self.token,
                "intents": self.intents.value,
                "properties": {"os": platform, "browser": "retux", "device": "retux"},
            },
        )
        logger.debug("Sending an identification payload to the Gateway.")
        await self._send(payload)

    async def _resume(self):
        """Sends a resuming payload to the Gateway."""
        payload = _GatewayPayload(
            op=_GatewayOpCode.RESUME.value,
            d={
                "token": self.token,
                "session_id": self._meta.session_id,
                "seq": self._meta.seq,
            },
        )
        logger.debug("Sending a resuming payload to the Gateway.")
        await self._send(payload)

    async def _heartbeat(self):
        """Sends a heartbeat payload to the Gateway."""
        payload = _GatewayPayload(op=_GatewayOpCode.HEARTBEAT.value, d=self._meta.seq)

        # FIXME: Move towards a better solution for the heartbeat acknowledgement loop.
        # This is a really bad approach to fixing heartbeat timing, but this only fires
        # during the initialisation of the async context manager.
        # Please spare me Bluenix.

        logger.debug("Waiting the appropriate time for probable connection.")
        await sleep(1)

        while self._heartbeat_ack:
            logger.debug("Sending a heartbeat payload to the Gateway.")
            await self._send(payload)
            await sleep(self._meta.heartbeat_interval)

    async def request_guild_members(
        self,
        guild_id: Snowflake,
        *,
        query: NotNeeded[str] = MISSING,
        limit: NotNeeded[int] = MISSING,
        presences: NotNeeded[bool] = MISSING,
        user_ids: NotNeeded[Snowflake | list[Snowflake]] = MISSING,
        nonce: NotNeeded[str] = MISSING,
    ):
        """
        Sends a request for all guild members to the Gateway.

        Parameters
        ----------
        guild_id : `Snowflake`
            The ID of the guild to request from.
        query : `str`, optional
            The name of the guild member(s). If you're looking to
            receive all members of a guild, this is left untouched.
        limit : `int`, optional
            How many guild members you wish to return. When `query`
            is specified, only a maximum of `100` are returned.
            This should be left untouched with `query` for all
            members of a guild.
        presences : `bool`, optional
            Whether you only want to receive guild members with
            a presence. The `GUILD_PRESENCES` intent must be
            enabled in order to use.
        user_ids : `Snowflake` or `list[Snowflake]`, optional
            The IDs of members in the guild to return. This
            may be used in conjunction to `query`, and poses the
            same maximum as `limit` regardless of declaration.
        nonce : `str`, optional
            A nonce used for identification when receiving a
            `Guild Members Chunk` event.
        """
        payload = _GatewayPayload(
            op=_GatewayOpCode.REQUEST_GUILD_MEMBERS,
            d={
                "guild_id": guild_id,
                "query": "" if query is MISSING else query,
                "limit": 0 if limit is MISSING else limit,
            },
        )

        if presences is not MISSING:
            payload.data["presences"] = presences
        if user_ids is not MISSING:
            payload.data["user_ids"] = user_ids
        if nonce is not MISSING:
            payload.data["nonce"] = nonce

        logger.debug("Sending a payload requesting for guild members to the Gateway.")
        await self._send(payload)

    async def update_voice_state(
        self,
        guild_id: Snowflake,
        channel_id: NotNeeded[Snowflake] = MISSING,
        self_mute: NotNeeded[bool] = MISSING,
        self_deaf: NotNeeded[bool] = MISSING,
    ):
        """
        Sends a request updating the bot's voice state to the Gateway.

        Parameters
        ----------
        guild_id : `Snowflake`
            The ID of the guild to request from.
        channel_id : `Snowflake`, optional
            The channel ID of the guild to update in.
            If the bot is trying to disconnect, this should
            be left untouched.
        self_mute : `bool`, optional
            Whether the bot is muting itself or not.
            Defaults to `False`.
        self_deaf : `bool`, optional
            Whether the bot is deafening itself or not.
            Defaults to `False`.
        """
        payload = _GatewayPayload(
            op=_GatewayOpCode.VOICE_STATE_UPDATE,
            d={
                "guild_id": guild_id,
                "channel_id": None if channel_id is MISSING else channel_id,
                "self_mute": False if self_mute is MISSING else self_mute,
                "self_deaf": False if self_deaf is MISSING else self_deaf,
            },
        )
        logger.debug("Sending a payload requesting a voice state update to the Gateway.")
        await self._send(payload)

    @property
    def latency(self) -> float:
        """
        The calculated difference between the last known set
        of acknowledgements for a Gateway event.
        """
        return self._last_ack[1] - self._last_ack[0]
