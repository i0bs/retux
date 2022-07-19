from attrs import define, field

from ...client.resources.abc import Partial

from .abc import Event


@define(kw_only=True)
class Ready(Event):
    """
    Represents when the client has successfully connected.

    Attributes
    ----------
    v : `int`
        The used version of the Discord API.
    session_id : `str`
        The ID of the bot's Gateway connection session,
        used for reconnection.
    shard : `list[int]`, optional
        The shards of the Gateway connection, if present.
    application : `Partial`
        The application form of the bot.
        Contains only `id` and `flags`.

    Methods
    -------
    version : `int`
        The used version of the Discord API.
    """

    v: int = field()
    """The used version of the Discord API."""
    # TODO: implement User object
    # user: User = field(converter=User)
    # """The user form of the bot application."""
    # TODO: implement Unavailable Guild object
    # guilds: list[dict] | list[UnavailableGuild] = field(converter=list)
    # """The guilds unavailable to the bot."""
    session_id: str = field()
    """The ID of the bot's Gateway connection session, used for reconnection."""
    shard: list[int] | None = field(converter=list, default=None)
    """The shards of the Gateway connection, if present."""
    application: dict | Partial = field(converter=Partial)
    """The application form of the bot. Contains only `id` and `flags`."""

    @property
    def version(self) -> int:
        """The used version of the Discord API."""
        return self.v


@define(kw_only=True)
class Resumed(Event):
    """
    Represents when the client has successfully resumed a connection.

    Attributes
    ----------
    token : `str`
        The token of the bot used.
    session_id : `str`
        The ID of the Gateway connection session.
    seq : `int`
        The last sequence number given for the session.
    """

    token: str = field()
    """The token of the bot used."""
    session_id: str = field()
    """The ID of the Gateway connection session."""
    seq: int = field()
    """The last sequence number given for the session."""


@define()
class Reconnect(Event):
    """
    Represents when the client has been told to reconnect.

    ---

    It should be noted that reconnection is **automatically handled for you**
    in retux already. This event should never be used outside of logging down
    when reconnections were made. Do not use this event to force a reconnection
    unless you know what you're doing!
    """


@define(repr=False)
class InvalidSession(Event):
    """
    Represents when the client has an invalidated Gateway connection.

    ---

    Invalid sessions are determined by one of three factors:

    - The Gateway could not resume the connection.
    - The client could not identify itself correctly.
    - The Gateway has invalidated the session for you, and requires a new connection.

    ---

    Attributes
    ----------
    _invalid_session : `bool`
        Whether the session can be reconnected to or not.
        This should never need to be called upon directly.
        Please use the representation of the class itself.

        This defaults to `False` and determined on good faith
        of ensuring a stable connection over potential client
        conflict.

    Methods
    -------
    can_reconnect() : `bool`
        Checks the session to see if a reconnection is possible.
    """

    _invalid_session: bool = field(default=False)
    """
    Whether the session can be reconnected to or not.
    This should never need to be called upon directly.
    Please use the representation of the class itself.

    This defaults to `False` and determined on good faith
    of ensuring a stable connection over potential client
    conflict.
    """

    def __repr__(self) -> bool:
        return self._invalid_session

    def can_reconnect(self) -> bool:
        """
        Checks the session to see if a reconnection is possible.

        Returns
        -------
        `bool`
            Whether the session can be reconnected to or not.
        """
        return self._invalid_session
