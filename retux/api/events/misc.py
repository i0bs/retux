from datetime import datetime
from attrs import define, field

from ...client.resources.abc import Snowflake
from ...utils.converters import optional_c


@define()
class TypingStart:
    """
    Represents a `TYPING_START` event from Discord.

    ---

    Sent when a user starts typing in a channel.

    ---

    Attributes
    ----------
    channel_id : `Snowflake`
        The ID of the channel when typing occured.
    user_id : `Snowflake`
        The ID of the user who started typing.
    timestamp : `datetime.datetime`
        The timestamp of when the typing occured.
    guild_id : `Snowflake`, optional
        The ID of the guild when typing occured.

        This will only appear when a user is typing
        outside of a DM.
    """

    channel_id: str | Snowflake = field(converter=Snowflake)
    """The ID of the channel when typing occured."""
    user_id: str | Snowflake = field(converter=Snowflake)
    """The ID of the user who started typing."""
    timestamp: int | datetime = field(converter=datetime.fromtimestamp)
    """The timestamp of when the typing occured."""
    guild_id: str | Snowflake | None = field(converter=optional_c(Snowflake), default=None)
    """
    The ID of the guild when typing occured.

    This will only appear when a user is typing
    outside of a DM.
    """
    # TODO: implement Member object.
    # member: Member = field(converter=Member, default=None)
