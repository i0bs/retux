from attrs import define, field
from .abc import Object, Snowflake
from .user import User
from .role import Role
from ...utils import optional_c, list_c


@define()
class Emoji(Object):
    """
    Represents an Emoji from Discord.

    Attributes
    ----------
    id : `Snowflake`, optional
        The ID of the Emoji.

        Only available on guild created emojis.
    name : `str`, optional
        The name of the emoji.

        This is a unicode emoji if the emoji
        is standard, otherwise it is the name
        of the emoji.
    user : `User`, optional
        The user that created the emoji.
    require_colons : `bool`, optional
        Whether or not the emoji needs to be wrapped in colons.
    managed : `bool`, optional
        Whether or not the emoji is managed.
    animated : `bool`, optional
        Whether or not the emoji is animated.
    available : `bool`
        Whether or not the emoji is available.

        Defaults to `False` if the server that owns
        the emoji lost a level of boosting.
    """

    id: str | Snowflake | None = field(converter=optional_c(Snowflake), default=None)
    """
    The ID of the Emoji.

    Only available on guild created emojis.
    """
    name: str | None = field(default=None)
    """
    The name of the emoji.

    This is a unicode emoji if the emoji
    is standard, otherwise it is the name
    of the emoji.
    """
    roles: list[dict] | list[Role] | None = field(converter=optional_c(list_c(Role)))
    """A list of roles allowed to use this emoji."""
    user: dict | User | None = field(converter=optional_c(User))
    """The user that created the emoji."""
    require_colons: bool | None = field(default=None)
    """Whether or not the emoji needs to be wrapped in colons."""
    managed: bool | None = field(default=None)
    """Whether or not the emoji is managed."""
    animated: bool | None = field(default=None)
    """Whether or not the emoji is animated."""
    available: bool = field(default=False)
    """
    Whether or not the emoji is available.

    Defaults to `False` if the server that owns
    the emoji lost a level of boosting.
    """
