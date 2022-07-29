from .abc import Snowflake, Object
from ...utils.converters import optional_c

from attrs import define, field


__all__ = (
    "Role",
    "RoleTags",
)


@define(kw_only=True)
class RoleTags:
    """
    Represents the tags of a role from Discord.

    Attributes
    ----------
    bot_id : `Snowflake`, optional
        The ID of the bot this role belongs to.
    integration_id : `Snowflake`, optional
        The ID of the integration this role belongs to.
    premium_subscriber : `bool`
        Whether this is the guild's premium subscriber role.
    """

    bot_id: Snowflake | str | None = field(converter=optional_c(Snowflake))
    """The id of the bot this role belongs to."""
    integration_id: Snowflake | str | None = field(converter=optional_c(Snowflake))
    """The id of the integration this role belongs to."""
    premium_subscriber: bool = field(default=False)
    """Whether this is the guild's premium subscriber role."""


@define(kw_only=True)
class Role(Object):
    """
    Represents a role from Discord.

    Attributes
    ----------
    id : `Snowflake`
        The ID of the role.
    name : `str`
        The name of the role.
    color : `int`
        The integer representation of hexadecimal color code of the role.
    hoist : `bool`
        If this role is pinned in the user listing.
    icon : `str`, optional
        The hash of the roles icon, if present.
    unicode_emoji : `str`, optional
        The emoji unicode of the role, if present.
    position : `int`
        The position of the role.
    permissions : `str`
        The role's permission bit set.
    managed : `bool`
        Whether this role is managed by an integration.
    tags : `RoleTags`, optional
        The tags this role has, if present.
    """

    id: Snowflake | str = field(converter=Snowflake)
    """The ID of the role."""
    name: str = field()
    """The name of the role."""
    color: int = field()
    """The integer representation of hexadecimal color code of the role."""
    hoist: bool = field()
    """If this role is pinned in the user listing."""
    icon: str | None = field(default=None)
    """The role icon hash, if present."""
    unicode_emoji: str | None = field(default=None)
    """The emoji unicode of the role, if present."""
    position: int = field()
    """The position of the role."""
    permissions: str = field()
    """The role's permission bit set."""
    managed: bool = field()
    """Whether this role is managed by an integration."""
    mentionable: bool = field()
    """Whether this role is mentionable."""
    tags: RoleTags | None = field(converter=optional_c(RoleTags))
    """The tags this role has, if present."""
