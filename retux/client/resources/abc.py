from datetime import datetime
from typing import Union

from attrs import define, field

from ...const import MISSING


@define(slots=False)
class Event:
    """An abstract base class for representing Gateway events."""

    name: str = field()
    bot: "Bot" | MISSING = field(default=MISSING)  # noqa


@define(repr=False, eq=False)
class Snowflake:
    """
    Represents an unique identifier for a Discord resource.

    ---

    Discord utilizes Twitter's snowflake format for uniquely identifiable descriptors
    (IDs). These IDs are guaranteed to be unique across all of Discord, except in some
    unique scenarios in which child objects share their parent's ID.

    ---

    Attributes
    ----------
    _snowflake : `str`, `int`
        The snowflake itself. This should never need to be called upon directly.
        Please use the representation of the class itself.

    Methods
    -------
    timestamp : `datetime.datetime`
        The timestamp of the snowflake as a UTC-native datetime.

        Timestamps are denoted as milliseconds since the Discord Epoch:
        the first second of 2015, or or `1420070400000`.
    worker_id : `int`
        The internal worker ID of the snowflake.
    process_id : `int`
        The internal process ID of the snowflake.
    increment : `int`
        The internal incrementation number of the snowflake.

        This value will only increment when a process has been
        generated on this snowflake, e.g. a resource.
    """

    _snowflake: str | int = field(converter=str)
    """The internally stored snowflake. Snowflakes are always in a string-form."""

    def __repr__(self) -> str:
        return str(self._snowflake)

    def __eq__(self, other: Union[str, int, "Snowflake"]) -> bool:
        if type(other) == int:
            return bool(int(self._snowflake) == other)
        else:
            return bool(self._snowflake == str(other))

    @property
    def timestamp(self) -> datetime:
        """
        The timestamp of the snowflake as a UTC-native datetime.

        Timestamps are denoted as milliseconds since the Discord Epoch:
        the first second of 2015, or `1420070400000`.
        """
        retrieval: int | float = (int(self._snowflake) >> 22) + 1420070400000
        return datetime.utcfromtimestamp(retrieval)

    @property
    def worker_id(self) -> int:
        """The internal worker ID of the snowflake."""
        return (int(self._snowflake) & 0x3E0000) >> 17

    @property
    def process_id(self) -> int:
        """The internal process ID of the snowflake."""
        return (int(self._snowflake) & 0x1F000) >> 12

    @property
    def increment(self) -> int:
        """
        The internal incrementation number of the snowflake.

        This value will only increment when a process has been
        generated on this snowflake, e.g. a resource.
        """
        return int(self._snowflake) & 0xFFF


@define()
class Component:
    """
    Represents the base information of a component from Discord.

    ---

    `custom_id` is an attribute shared in every component,
    however, only `Button` makes them optional. A custom ID is
    a developer-defined ID in-between 1-100 characters.
    """
