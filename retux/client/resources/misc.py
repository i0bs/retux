from attrs import define, field
from datetime import datetime


@define(repr=False, eq=False)
class Snowflake:
    """
    Represents an unique identifier for a Discord resource.

    Discord utilizes Twitter's snowflake format for uniquely identifiable descriptors
    (IDs). These IDs are guaranteed to be unique across all of Discord, except in some
    unique scenarios in which child objects share their parent's ID.

    ---

    When a `Snowflake` is compared, its base representation will always be in string
    format. If you want to treat the snowflake as an integer, you must manually convert
    it.
    """

    _snowflake: str | int = field(converter=str)
    """The internally stored snowflake. Snowflakes are always in a string-form."""

    def __repr__(self) -> str:
        return str(self._snowflake)

    def __eq__(self, other: str | int | "Snowflake") -> bool:
        return bool(self.__repr__() == str(other))

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
    def worker_id(self) -> int | float:
        """The internal worker ID of the snowflake."""
        return (int(self._snowflake) & 0x3E0000) >> 17

    @property
    def process_id(self) -> int | float:
        """The internal process ID of the snowflake."""
        return (int(self._snowflake) & 0x1F000) >> 12

    @property
    def increment(self) -> int | float:
        """
        The internal incrementation number of the snowflake.

        This value will only increment when a process has been
        generated on this snowflake, e.g. a resource.
        """
        return int(self._snowflake) & 0xFFF
