from enum import IntFlag
from aenum import IntEnum
from attrs import define, field

from .abc import Object, Partial, Snowflake

from ...utils.converters import optional_c, list_c


@define(kw_only=True)
class WelcomeScreenChannel:
    """
    Represents a channel shown in the welcome screen of a guild from Discord.

    Attributes
    ----------
    channel_id : `Snowflake`
        The ID of the channel shown.
    description : `str`
        A description shown with the channel.
    emoji_id : `Snowflake`, optional
        The ID of the emoji if it isn't a unicode.
    emoji_name : `str`, optional
        The name of the emoji, if present.
    """

    channel_id: str | Snowflake = field(converter=Snowflake)
    """The ID of the channel shown."""
    description: str = field()
    """A description shown with the channel."""
    emoji_id: str | Snowflake | None = field(converter=Snowflake, default=None)
    """The ID of the emoji if it isn't a unicode."""
    emoji_name: str | None = field(default=None)
    """The name of the emoji, if present."""

    # TODO: implement Emoji object.
    # @property
    # def emoji(self) -> Emoji:
    #     return Emoji(id=emoji_id, name=emoji_name)


@define(kw_only=True)
class WelcomeScreen:
    """
    Represents the welcome screen in a guild from Discord.

    Attributes
    ----------
    description : `str`
        The description of the guild in the welcome screen.
    welcome_channels : `list[WelcomeScreenChannel]`, optional
        The channels show in the welcome screen. A maximum
        of `5` are able to be shown.

    Methods
    -------
    channels : `list[WelcomeScreenChannel]`, optional
        The channels show in the welcome screen. A maximum
        of `5` are able to be shown.
    """

    description: str | None = field(default=None)
    """The description of the guild in the welcome screen."""
    welcome_channels: list[dict] | list[WelcomeScreenChannel] | None = field(
        converter=optional_c(list_c(WelcomeScreenChannel)), default=None
    )
    """
    The channels show in the welcome screen. A maximum
    of `5` are able to be shown.
    """

    @property
    def channels(self) -> list[WelcomeScreenChannel] | None:
        """
        The channels show in the welcome screen. A maximum
        of `5` are able to be shown.
        """
        return self.welcome_channels


class SystemChannelFlags(IntFlag):
    """
    System channel flags are a set of bitwise values that represent
    the flags of a guild's welcome channel.
    """

    SUPPRESS_JOIN_NOTIFICATIONS = 1 << 0
    """Suppresses welcome messages from the channel."""
    SUPPRESS_PREMIUM_SUBSCRIPTIONS = 1 << 1
    """Suppresses server boosting messages from the channel."""
    SUPPRESS_GUILD_REMINDER_NOTIFICATIONS = 1 << 2
    """Suppresses server setup tips from the channel."""
    SUPPRESS_JOIN_NOTIFICATION_REPLIES = 1 << 3
    """Suppresses sticker reply popouts from the channel."""


class GuildNSFWLevel(IntEnum):
    """
    Represents the levels of NSFW filtering in a guild from Discord.

    Constants
    ---------
    DEFAULT
        There is a some filtering going on.
    EXPLICIT
        The guild is being checked for explicit NSFW content.
    SAFE
        The guild is not being checked for NSFW.
    AGE_RESTRICTED
        The guild is checked on parallel to `EXPLICIT` with
        verification required.
    """

    DEFAULT = 0
    """There is a some filtering going on."""
    EXPLICIT = 1
    """The guild is being checked for explicit NSFW content."""
    SAFE = 2
    """The guild is not being checked for NSFW."""
    AGE_RESTRICTED = 3
    """
    The guild is checked on parallel to `EXPLICIT` with
    verification required.
    """


class ExplicitContentFilterLevel(IntEnum):
    """
    Represents the explicit content filter levels of a guild
    from Discord.

    Constants
    ---------
    DISABLED
        Content is not being checked for explicit content.
    MEMBERS_WITHOUT_ROLES
        Content is being checked only from guild members
        without roles.
    ALL_MEMBERS
        Content is being checked from evey guild member.
    """

    DISABLED = 0
    """Content is not being checked for explicit content."""
    MEMBERS_WITHOUT_ROLES = 1
    """Content is being checked only from guild members without roles."""
    ALL_MEMBERS = 2
    """Content is being checked from evey guild member."""


class VerificationLevel(IntEnum):
    """
    Represents the verification levels of a guild from Discord.

    Constants
    ---------
    NONE
        There is no verification standard set.
    LOW
        Guild members must have their e-mail verified.
    MEDIUM
        Guild members must have been registered on Discord for longer than 5 minutes.
    HIGH
        Guild members must be part of the guild for longer than 10 minutes.
    VERY_HIGH
        Guild members must have their phone number verified.
    """

    NONE = 0
    """There is no verification standard set."""
    LOW = 1
    """Guild members must have their e-mail verified."""
    MEDIUM = 2
    """Guild members must have been registered on Discord for longer than 5 minutes."""
    HIGH = 3
    """Guild members must be part of the guild for longer than 10 minutes."""
    VERY_HIGH = 4
    """Guild members must have their phone number verified."""


@define(repr=False, kw_only=True)
class UnavailableGuild(Partial, Object):
    """
    Represents an unavailable guild from Discord.

    Attributes
    ----------
    id : `Snowflake`
        The ID of the unavailable guild.
    unavailable : `bool`
        Whether the guild is unavailable or not.
        This is always set to `True` unless Discord
        says otherwise from a given payload. Use
        the class representation itself for this.
    """

    id: str | Snowflake = field(converter=Snowflake)
    unavailable: bool = field(default=True)

    def __repr__(self) -> bool:
        return self.unavailable


@define(kw_only=True)
class Guild(Object):
    """
    Represents a guild from Discord.


    Attributes
    ----------
    id : `Snowflake`
        The ID of the guild.
    name : `str`
        The name of the guild.
    icon : `str`
        The icon of the guild in a URL format.
    owner_id : `Snowflake`
        The ID of the owner of the guild.
    afk_timeout : `int`
        The current set AFK timeout in seconds for the guild.
    verification_level : `VerificationLevel`
        The set verification level for members of the guild.
    default_message_notifications : `int`
        The default notifications level of the guild.
    explicit_content_filter : `ExplicitContentFilterLevel`
        The explicit content filter level of the guild.
    features : `list[str]`
        The currently enabled features inside of the guild.
    mfa_level : `int`
        The required MFA (rep. by 2FA) level of the guild.
    system_channel_flags : `SystemChannelFlags`
        The guild's welcome channel's flags for suppression.
    premium_tier : `int`
        The current server boosting tier level of the guild.
    preferred_locale : `str`
        The preferred locale of the guild.
    nsfw_level : `int`
        The currently set NSFW level of the guild.
    premium_progress_bar_enabled : `bool`
        Whether the guild has the server boosting bar enabled or not.
    owner : `bool`
        Whether the user who invoked the guild is the owner or not.
    afk_channel_id : `Snowflake`, optional
        The ID of the AFK channel inside the guild, if present.
    icon_hash : `str`, optional
        The icon of the guild in a hash format.

        This hash is pre-determined by the API and does not reflect
        the URL path.
    splash : `str`, optional
        The hash of the guild's splash invite screen image, if present.
    discovery_splash : `str`, optional
        The hash of the guild's discovery splash screen image, if present.
    permissions : `str`, optional
        The calculated permissions of the user invoking the guild, if present.
    region : `str`, optional
        The ID of the voice region for the guild.

        This field has been deprecated as of `v8` and should no longer
        be used.
    widget_enabled : `bool`
        Whether the server has its widget enabled or not.
    widget_channel_id : `Snowflake`, optional
        The ID of the channel which the widget targets, if present.
    application_id : `Snowflake`, optional
        The ID of the application for the guild if created via. a bot.
    system_channel_id : `Snowflake`, optional
        The ID of the system welcome messages channel, if present.
    rules_channel_id : `Snowflake`, optional
        The ID of the rules channel, if presently determined as a Community server.
    max_presences : `int`, optional
        The maximum amount of presences allowed in the guild. Always set to `0`
        underneath a guild size cap.
    max_members : `int`, optional
        The maximum amount of members allowed in the guild.
        Globally set to `800000` currently.
    vanity_url_code : `str`, optional
        The vanity URL of the guild, if present.
    description : `str`, optional
        The description of the guild, if presently determined as a Community server.
    banner : `str`, optional
        The banner of the guild, if present.
    premium_subscription_count : `int`, optional
        The approximated count of boosts the guild has.
    public_updates_channel_id : `Snowflake`, optional
        The community moderation-only ID of the channel in the guild, if present.
    max_video_channel_users : `int`
        The maximum amount of users in a voice channel allowed to have video on.
        Globally set to `25` currently.
    approximate_member_count : `int`, optional
        The approximated member count of the guild.
    approximate_presence_count : `int`, optional
        The approxiated amount of presences in the guild.
    welcome_screen : `WelcomeSceren`, optional
        The welcome screen of the guild, if present.
    """

    id: str | Snowflake = field(converter=Snowflake)
    """The ID of the guild."""
    name: str = field()
    """The name of the guild."""
    icon: str = field()
    """The icon of the guild in a URL format."""
    owner_id: str | Snowflake = field(converter=Snowflake)
    """The ID of the owner of the guild."""
    afk_timeout: int = field()
    """The current set AFK timeout in seconds for the guild."""
    verification_level: int | VerificationLevel = field(converter=VerificationLevel)
    """The set verification level for members of the guild."""
    default_message_notifications: int = field()
    """The default notifications level of the guild."""
    explicit_content_filter: int | ExplicitContentFilterLevel = field(
        converter=ExplicitContentFilterLevel
    )
    """The explicit content filter level of the guild."""
    features: list[str] = field()
    """The currently enabled features inside of the guild."""
    mfa_level: int = field()
    """The required MFA (rep. by 2FA) level of the guild."""
    system_channel_flags: int | SystemChannelFlags = field(converter=SystemChannelFlags)
    """The guild's welcome channel's flags for suppression."""
    premium_tier: int = field()
    """The current server boosting tier level of the guild."""
    preferred_locale: str = field()
    """The preferred locale of the guild."""
    nsfw_level: int = field()
    """The currently set NSFW level of the guild."""
    premium_progress_bar_enabled: bool = field()
    """Whether the guild has the server boosting bar enabled or not."""
    owner: bool = field(default=False)
    """Whether the user who invoked the guild is the owner or not."""
    afk_channel_id: str | Snowflake | None = field(converter=optional_c(Snowflake), default=None)
    """The ID of the AFK channel inside the guild, if present."""
    icon_hash: str | None = field(default=None)
    """
    The icon of the guild in a hash format.

    This hash is pre-determined by the API and does not reflect
    the URL path.
    """
    splash: str | None = field(default=None)
    """The hash of the guild's splash invite screen image, if present."""
    discovery_splash: str | None = field(default=None)
    """The hash of the guild's discovery splash screen image, if present."""
    permissions: str | None = field(default=None)
    """The calculated permissions of the user invoking the guild, if present."""
    region: str | None = field(default=None)
    """
    The ID of the voice region for the guild.

    This field has been deprecated as of `v8` and should no longer
    be used.
    """
    widget_enabled: bool = field(default=False)
    """Whether the server has its widget enabled or not."""
    widget_channel_id: str | Snowflake | None = field(converter=optional_c(Snowflake), default=None)
    """The ID of the channel which the widget targets, if present."""
    # TODO: implement Role object.
    # roles: list[dict] | list[Role] = field(converter=Role, default=None)
    # TODO: implement Emoji object.
    # emojis: list[dict] | list[Emoji] | None = field(converter=Emoji, default=None)
    application_id: str | Snowflake | None = field(converter=optional_c(Snowflake), default=None)
    """The ID of the application for the guild if created via. a bot."""
    system_channel_id: str | Snowflake | None = field(converter=optional_c(Snowflake), default=None)
    """The ID of the system welcome messages channel, if present."""
    rules_channel_id: str | Snowflake | None = field(converter=optional_c(Snowflake), default=None)
    """The ID of the rules channel, if presently determined as a Community server."""
    max_presences: int | None = field(default=None)
    """
    The maximum amount of presences allowed in the guild. Always set to `0`
    underneath a guild size cap."""
    max_members: int | None = field(default=None)
    """The maximum amount of members allowed in the guild.
    Globally set to `800000` currently.
    """
    vanity_url_code: str | None = field(default=None)
    """The vanity URL of the guild, if present."""
    description: str | None = field(default=None)
    """The description of the guild, if presently determined as a Community server."""
    banner: str | None = field(default=None)
    """The banner of the guild, if present."""
    premium_subscription_count: int | None = field(default=None)
    """The approximated count of boosts the guild has."""
    public_updates_channel_id: str | Snowflake | None = field(
        converter=optional_c(Snowflake), default=None
    )
    """The community moderation-only ID of the channel in the guild, if present."""
    max_video_channel_users: int = field(default=25)
    """
    The maximum amount of users in a voice channel allowed to have video on.
    Globally set to `25` currently.
    """
    approximate_member_count: int | None = field(default=None)
    """The approximated member count of the guild."""
    approximate_presence_count: int | None = field(default=None)
    """The approxiated amount of presences in the guild."""
    welcome_screen: dict | WelcomeScreen | None = field(
        converter=optional_c(WelcomeScreen), default=None
    )
    """The welcome screen of the guild, if present."""
    # TODO: implement Sticker object.
    # stickers: list[dict] | list[Sticker] | None = field(converter=Sticker, default=None)
