from enum import Enum
from json import dumps, loads
from logging import getLogger
from sys import platform
from time import perf_counter
from typing import Any, Protocol

from attrs import define, field, fields_dict
from cattrs import structure_attrs_fromdict
from trio import sleep_until
from trio_websocket import ConnectionClosed, WebSocketConnection, open_websocket_url

from ..client.flags import Intents
from ..const import MISSING, __gateway_url__

logger = getLogger("retux.api.gateway")


@define()
class _GatewayMeta:
    """
    Represents metadata for a Gateway connection.

    Attributes
    ----------
    version : `int`
        The version of the Gateway.
    encoding : `str`
        The encoding type on Gateway payloads.
    compress : `str`, optional
        The compression type on Gateway payloads.
    heartbeat_interval : `float`, optional
        The interval at which a heartbeat is sent.
    session_id : `str`, optional
        The ID of an existent session, used for when resuming a lost connection.
    seq : `int`, optional
        The sequence number on an existent session.
    """

    version: int = field()
    """The version of the Gateway."""
    encoding: str = field()
    """The encoding type on Gateway payloads."""
    compress: str = field(default=None)
    """The compression type on Gateway payloads."""
    heartbeat_interval: float = field(default=MISSING)
    """The interval at which a heartbeat is sent."""
    session_id: str = field(default=None)
    """The ID of an existent session, used for when resuming a lost connection."""
    seq: int = field(default=None)
    """The sequence number on an existent session."""


class _GatewayOpCode(Enum):
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

    ---

    Attributes
    ----------
    op (opcode) : `_GatewayOpCode`
        The opcode of the payload.
    d (data) : `typing.Any`
        The payload's event data.
    s (sequence) : `int`, optional
        The sequence number, used for resuming sessions and heartbeats.
    t (name) : `str`, optional
        The name of the payload's event.
    """

    op: _GatewayOpCode = field(converter=_GatewayOpCode)
    """The opcode of the payload."""
    d: Any = field(default=None)
    """The payload's event data."""
    s: int = field(default=None)
    """The sequence number, used for resuming sessions and heartbeats."""
    t: str = field(default=None)
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
        compress: str = MISSING,
    ):
        ...

    async def _receive(self) -> _GatewayPayload:
        ...

    async def _send(self, payload: _GatewayPayload):
        ...

    async def connect(self):
        ...

    async def _track(self, payload: _GatewayPayload):
        ...

    async def _identify(self):
        ...

    async def _resume(self):
        ...

    async def _heartbeat(self, heartbeat_interval: float):
        ...

    @property
    def latency(self):
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
    _last_ack : `tuple[float]`
        The before/after time of the last Gateway event tracked. See `latency` for Gateway connection timing.
    """

    # TODO: Add sharding and presence changing.
    # TODO: Add dispatcher regulation standard.
    # TODO: Add voice state changing
    # TODO: Add request member ability.

    __slots__ = ("token", "intents", "_conn", "_meta", "_closed", "_last_ack")
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
    _last_ack: tuple[float]
    """The before/after time of the last Gateway event tracked. See `latency` for Gateway connection timing."""

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

    async def _receive(self) -> _GatewayPayload:
        """
        Receives the next incoming payload from the Gateway.

        Returns
        -------
        `_GatewayPayload`
        """

        # We're standardising every response from
        # the WebSocket server to be in a payload class form.
        # this allows an easier and more abstracted approach
        # to handling it without an utter dict mess.

        # FIXME: our exception handling neglects other rejection
        # reasons. A more thorough analysis of trio_websocket
        # is necessary to have an extensible exception of our
        # own for clarifying connection loss.

        try:
            resp = await self._conn.get_message()
            json = loads(resp)
            return structure_attrs_fromdict(json, _GatewayPayload)
        except ConnectionClosed:
            logger.fatal("The connection to Discord's Gateway has closed.")
            self._closed = True
            await self.connect()

    async def _send(self, payload: _GatewayPayload):
        """
        Sends a payload to the Gateway.

        Parameters
        ----------
        payload : `_GatewayPayload`
            The payload to send.
        """

        # trio_websocket requires for us to send all data
        # in the form of a string or set of bytes. In our case,
        # it would be better to send a serialised JSON string
        # so we run into no risks.

        # TODO: allow another compression types to interpret
        # in the form of bytes.

        try:
            json = dumps(fields_dict(payload))
            resp = await self._conn.send_message(json)  # noqa
        except ConnectionClosed:
            logger.fatal("The connection to Discord's Gateway has closed.")
            self._closed = True
            await self.connect()

    async def connect(self):
        """Connects to the Gateway and initiates a WebSocket state."""
        self._last_ack = (perf_counter(), perf_counter())
        self._conn = None

        # FIXME: this connection type will only work with JSON in mind.
        # if other compression or encoding types are supplied, they
        # will not be properly digested. This is only added so others
        # may modify their GatewayClient to their liking.

        async with open_websocket_url(
            f"{__gateway_url__}?v={self._meta.version}&encoding={self._meta.encoding}"
            f"&compress={'' if self._meta.compress is None else self._meta.compress}"
        ) as self._conn:
            self._closed = self._conn.closed

            if self._closed:
                await self.connect()

            while not self._closed:
                data = await self._receive()

                if self._conn is None:
                    await self.connect()
                    break

                if data:
                    await self._track(data)

    async def _track(self, payload: _GatewayPayload):
        """
        Tracks data sent from the Gateway and interprets it.

        Parameters
        ----------
        payload : `_GatewayPayload`
            The payload being sent from the Gateway.
        """
        logger.debug(
            f"Tracking payload: {payload.opcode}{'.' if payload.name is None else ', data is present.'}"
        )

        match payload.opcode:
            case _GatewayOpCode.HELLO:
                self._meta.heartbeat_interval = payload.data.get("heartbeat_interval") / 1000
                await self._heartbeat(self._meta.heartbeat_interval)

                logger.debug("A heartbeat has been started.")

                if not self._meta.session_id:
                    await self._identify()
                else:
                    await self._resume()
            case _GatewayOpCode.HEARTBEAT:

                # trio_websocket allows us to treat a send_message()
                # call as a blocking condition and waive it. In coordination
                # with sleep_until for exact time execution, we're able to
                # use this to our advantage for perfected heartbeats.

                await self._heartbeat(self._meta.heartbeat_interval)
            case _GatewayOpCode.HEARTBEAT_ACK:

                # FIXME: this may produce inaccurate results if multiple
                # events come into contact later on with additional _last_ack
                # declarations.

                self._last_ack[1] = perf_counter()
                logger.debug(f"A heartbeat was acknowledged. Time took {self.latency}ms.")
                self._last_ack[0] = perf_counter()
            case _GatewayOpCode.INVALID_SESSION:
                self._meta.session_id = None
                await self.connect()
            case _GatewayOpCode.DISPATCH:

                # TODO: implement a dispatch call.
                # await self._dispatch(payload.name, payload.data)

                logger.debug(f"Dispatching the given payload: {payload.name}")
        match payload.name:
            case "RESUMED":
                logger.debug(
                    f"The connection was resumed. (session: {self._meta.session_id}, sequence: {self._meta.seq}"
                )
            case "READY":
                logger.debug("The Gateway has declared a ready connection.")

    # TODO: Look into a better way to send data for payload structuring
    # that doesn't necessarily mean a dict. This is perfectly fine, but,
    # I like something a tiny bit more abstracted so that we could allow
    # voice state and guild member request calls in the future in a nicer
    # manner.

    async def _identify(self):
        """Sends an identification payload to the Gateway."""
        payload = _GatewayPayload(
            op=_GatewayOpCode.IDENTIFY,
            d={
                "token": self.token,
                "intents": self.intents.value,
                "properties": {"os": platform, "browser": "retux", "device": "retux"},
            },
        )
        await self._send(payload)
        logger.debug("Sending an identification payload to the Gateway.")

    async def _resume(self):
        """Sends a resuming payload to the Gateway."""
        payload = _GatewayPayload(
            op=_GatewayOpCode.RESUME,
            d={
                "token": self.token,
                "session_id": self._meta.session_id,
                "seq": self._meta.seq,
            },
        )
        await self._send(payload)
        logger.debug("Sending a resuming payload to the Gateway.")

    async def _heartbeat(self, heartbeat_interval: float):
        """Sends a heartbeat payload to the Gateway."""
        payload = _GatewayPayload(op=_GatewayOpCode.HEARTBEAT, d=self._meta.seq)
        await self._send(payload)
        logger.debug("Sending a heartbeat payload to the Gateway.")
        await sleep_until(heartbeat_interval)

    @property
    def latency(self) -> float:
        """
        The calculated difference between the last known set
        of acknowledgements for a Gateway event.
        """
        return self._last_ack[1] - self._last_ack[0]
