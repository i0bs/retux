from attrs import define, field
from enum import IntFlag

from .abc import Snowflake


class ApplicationFlags(IntFlag):
    """Application flags are a set of bitwise values that represent the public flags of an application."""

    GATEWAY_PRESENCE = 1 << 12
    """The intent required for bots in 100 or more servers in order to receive presence_update events."""
    GATEWAY_PRESENCE_LIMITED = 1 << 13
    """The intent required for bots in under 100 servers in order to receive presence_update events, can be found in bot settings."""
    GATEWAY_GUILD_MEMBERS = 1 << 14
    """The intent required for bots in 100 or more servers in order to receive member-related events."""
    GATEWAY_GUILD_MEMBERS_LIMITED = 1 << 15
    """The intent required for bots in under 100 servers in order to receive member-related events, can be found in bot settings."""
    VERIFICATION_PENDING_GUILD_LIMIT = 1 << 16
    """Indicates unusual growth of an app that prevents verification."""
    EMBEDDED = 1 << 17
    """Indicates if an app is embedded within the Discord client (currently unavailable publicly)."""
    GATEWAY_MESSAGE_CONTENT = 1 << 18
    """The intent required for bots in 100 or more servers in order to receive message content"""
    GATEWAY_MESSAGE_CONTENT_LIMITED = 1 << 19
    """Intent required for bots in under 100 servers in order to receive message content, can be found in bot settings."""


@define(kwargs_only=True)
class InstallParams:
    """
    Represents the install parameters of an Application from Discord.

    Attributes
    ----------
    scopes : `list[str]`
        The scopes the application needs to join a server.
    permissions : `str`
        The permissions the bot requests be in the bot role.
    """

    scopes: list[str] = field()
    """The scopes the application needs to join a server."""
    permissions: str = field()
    """The permissions the bot requests be in the bot role."""


@define(kw_only=True)
class Application:
    """
    Represents an Application from Discord.

    Attributes
    ----------
    id : `Snowflake`
        The ID of the application.
    name : `str`
        The name of the application.
    icon : `str`
        The hash for the application's icon.
    description : `str`
        The description of the application.
    rpc_origins : `list[str]`, optional
        A list of rpc origin urls, if rpc is enabled.
    bot_public : `bool`
        False if only application owner can join the application's bot to guilds.
    bot_require_code_grant : `bool`
        True if the application's bot has the oauth2 code grant flow enabled.
    terms_of_service_url : `str`, optional
        The url for the application's terms of service.
    privacy_policy_url : `str`, optional
        The url for the application's privacy policy.
    owner : `User`, optional
        A partial user object representing the application owner.
    summary : `str`
        **Deprecated**. This is an empty string that will be removed in v11. Defaults to an empty string.
    verify_key : `str`
        The hex encoded key for verification in interactions and the gamesdk's getticket.
    team : `Team`
        A team object representing the team that the application belongs to.
    guild_id : `Snowflake`, optional
        The ID of the guild if the application is a game sold on Discord.
    primary_sku_id : `Snowflake`, optional
        The ID of the "game sku" if it exists and the application is a game sold on Discord.
    slug : `str`, optional
        The url slug that links to the application's store page if it is a game sold on Discord.
    cover_image : `str`, optional
        The hash for the default rich presence invite cover.

        This hash is pre-determined by the API and does not reflect
        the URL path.
    flags : `ApplicationFlags`, optional
        The public flags of the application.
    tags : `list[str]`, optional
        A maximum of 5 tags describing the content and functionality of the application.
    install_params : `InstallParams`, optional
        Settings for the application's default in-app authorization link.
    custom_install_url : `str`, optional
        The application's default custom authorization link.
    """

    # TODO: consider making icon hash a File object
    # TODO: implement User object
    # TODO: implement Team object
    id: str | Snowflake = field(converter=Snowflake)
    """The ID of the application."""
    name: str = field()
    """The name of the application."""
    icon: str = field()
    """The hash for the application's icon."""
    description: str = field()
    """The hash for the application's icon."""
    rpc_origins: list[str] | None = field(converter=list, default=None)
    """A list of rpc origin urls, if rpc is enabled."""
    bot_public: bool = field()
    """False if only application owner can join the application's bot to guilds."""
    bot_require_code_grant: bool = field()
    """True if the application's bot has the oauth2 code grant flow enabled."""
    terms_of_service_url: str | None = field(default=None)
    """The url for the application's terms of service."""
    privacy_policy_url: str | None = field(default=None)
    """The url for the application's privacy policy."""
    owner: dict | User | None = field(default=None, converter=User)  # noqa
    """A partial user object representing the application owner."""
    summary: str = field()
    """**Deprecated**. This is an empty string that will be removed in v11. Defaults to `""`"""
    verify_key: str = field()
    """The hex encoded key for verification in interactions and the gamesdk's getticket"""
    team: dict | Team = field(converter=Team)  # noqa
    """A team object representing the team that the application belongs to."""
    guild_id: str | Snowflake | None = field(default=None, converter=Snowflake)
    """The ID of the guild if the application is a sold game."""
    primary_sku_id: str | Snowflake | None = field(default=None, converter=Snowflake)
    """The ID of the "game sku" if it exists and the application is a game sold on Discord."""
    slug: str | None = field(default=None)
    """IThe url slug that links to the application's store page if it is a game sold on Discord."""
    cover_image: str | None = field(default=None)
    """
    The hash for the default rich presence invite cover.

    This hash is pre-determined by the API and does not reflect
    the URL path.
    """
    flags: int | ApplicationFlags | None = field(default=None, converter=ApplicationFlags)
    """The public flags of the application."""
    tags: list[str] | None = field(converter=list, default=None)
    """A maximum of 5 tags describing the content and functionality of the application."""
    install_params: dict | InstallParams | None = field(default=None, converter=InstallParams)
    """The settings for the application's default in-app authorization link."""
    custom_install_url: str | None = field(default=None)
    """The application's default custom authorization link."""
