from enum import IntEnum
from json import dumps, loads
from logging import getLogger
from sys import platform
from time import perf_counter
from typing import Any, Protocol

from attrs import asdict, define, field
from cattrs import structure_attrs_fromdict
from trio import sleep_until, open_nursery
from trio_websocket import ConnectionClosed, WebSocketConnection, open_websocket_url

from ..client.flags import Intents
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


@define()
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

    # TODO: look into seeing if property methods are still
    # allowed in attrs-decorated classes. I'm almost certain
    # that they're not, and if so, look into a wrapper class.

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
    _closed : `bool`
        Whether the Gateway connection is closed or not.
    _last_ack : `list[float]`
        The before/after time of the last Gateway event tracked. See `latency` for Gateway connection timing.
    _dispatched : `dict | None`
        Represents the last item dispatched.
    """

    # TODO: Add sharding and presence changing.
    # TODO: Add dispatcher regulation standard.
    # TODO: Add voice state changing
    # TODO: Add request member ability.

    __slots__ = ("token", "intents", "_conn", "_meta", "_last_ack")
    token: str
    """The bot's token."""
    intents: Intents
    """The intents to connect with."""
    _conn: WebSocketConnection
    """An instance of a connection to the Gateway."""
    _meta: _GatewayMeta
    """Metadata representing connection parameters for the Gateway."""
    _closed: bool = True
    """Whether the Gateway connection is closed or not."""
    _last_ack: list[float]
    """The before/after time of the last Gateway event tracked. See `latency` for Gateway connection timing."""
    _dispatched: object | None = None
    """Represents the last item dispatched."""

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
        self._tasks = None  # this is just for the nursery process with heartbeats.

    async def __aenter__(self):
        self._tasks = await open_nursery().__aenter__()
        self._tasks.start_soon(self.reconnect)
        self._tasks.start_soon(self._heartbeat)
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

        # TODO: allow another compression types to interpret
        # in the form of bytes.

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
            if self._closed:
                await self._conn.aclose()
                await self.reconnect()

            while not self._closed:
                data = await self._receive()

                if data:
                    await self._track(data)

    async def reconnect(self):
        """Reconnects to the Gateway and reinitiates a WebSocket state."""
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
            case _GatewayOpCode.HEARTBEAT_ACK:

                # FIXME: this may produce inaccurate results if multiple
                # events come into contact later on with additional _last_ack
                # declarations.

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
            clean_name = "".join([_.capitalize() for _ in name.split("_")[:-1]])
            resource = getattr(__import__("retux.client.resources"), clean_name)
        except AttributeError:
            resource = MISSING
            logger.info(f"The Gateway sent us {name} with no data class found.")

        self._dispatched = {"name": name, "data": resource}

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

        logger.debug("Sending a heartbeat payload to the Gateway.")
        while not self._closed:
            await self._send(payload)
            await sleep_until(self._meta.heartbeat_interval)

    @property
    def latency(self) -> float:
        """
        The calculated difference between the last known set
        of acknowledgements for a Gateway event.
        """
        return self._last_ack[1] - self._last_ack[0]
