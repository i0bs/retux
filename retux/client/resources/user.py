from enum import IntEnum, IntFlag
from attrs import define, field

from .abc import Snowflake, Object

__all__ = ("User", "UserFlags", "UserPremiumType")


class UserFlags(IntFlag):
    """User flags are a set of bitwise values that represent the public flags of a user."""

    STAFF = 1 << 0
    """This user is a Discord employee."""
    PARTNER = 1 << 1
    """This user is part of the Partnership program."""
    HYPESQUAD = 1 << 2
    """This user is part of the HypeSquad Events program."""
    BUG_HUNTER_LEVEL_1 = 1 << 3
    """This user has the first Bug Hunter level."""
    HYPESQUAD_ONLINE_HOUSE_1 = 1 << 6
    """This user is part of the HypeSquad Bravery house."""
    HYPESQUAD_ONLINE_HOUSE_2 = 1 << 7
    """This user is part of the HypeSquad Brilliance house."""
    HYPESQUAD_ONLINE_HOUSE_3 = 1 << 8
    """This user is part of the HypeSquad Balance house."""
    PREMIUM_EARLY_SUPPORTER = 1 << 9
    """This user is an early Nitro supporter."""
    TEAM_PSEUDO_USER = 1 << 10
    """This user represents a `Team` on Discord."""
    BUG_HUNTER_LEVEL_2 = 1 << 14
    """This user has the second Bug Hunter level."""
    VERIFIED_BOT = 1 << 16
    """This user is a bot whose verification passed."""
    VERIFIED_DEVELOPER = 1 << 17
    """This user is a verified bot developer."""
    CERTIFIED_MODERATOR = 1 << 18
    """This user is a certified moderator."""
    BOT_HTTP_INTERACTIONS = 1 << 19
    """This user is a bot that only intakes interaction endpoints."""


class UserPremiumType(IntEnum):
    """
    Represents the types of user premium levels on Discord.

    Constants
    ---------
    NONE
        This user has no premium subscription.
    NITRO_CLASSIC
        This user has the Nitro Classic subscription.
    NITRO
        This user has the Nitro Regular subscription.
    """

    NONE = 0
    """This user has no premium subscription."""
    NITRO_CLASSIC = 1
    """This user has the Nitro Classic subscription."""
    NITRO = 2
    """This user has the Nitro Regular subscription."""


@define(kw_only=True)
class User(Object):
    """
    Represents a user from Discord.

    ---

    Because a user's information can be accessed via. numerous methods,
    some information is marked as being optional, when in reality it
    cannot be accessed by conventional means. Only `verified` and `email`
    are `None` if either not set, or OAuth2 was used with the e-mail scope.

    ---

    Attributes
    ----------
    id : `Snowflake`
        The ID of the user.
    username : `str`
        The name of the user.
    discriminator : `str`
        The discriminator (4-digit tag) of the user.
    avatar : `str`, optional
        The hash of the user's avatar.
    bot : `bool`, optional
        Whether the user is a bot or not.
    system : `bool`, optional
        Whether the user is from the official Discord System or not.
    mfa_enabled : `bool`, optional
        Whether the user has 2FA (two-factor authentication) enabled
        or not.
    banner : `str`, optional
        The hash of the user's banner, if present.
    accent_color : `int`, optional
        The color of the user's banner, if present.
    locale : `str`, optional
        The user's selected locale, if present.
    verified : `bool`, optional
        Whether the user has a verified e-mail or not.
    email : `str`, optional
        The e-mail associated to the user's account, if present.
    flags : `UserFlags`, optional
        The public flags on the user's account, if present.
    premium_type : `int`, optional
        The type of Nitro subscription the user has.
    public_flags : `UserFlags`, optional
        The public flags on the user's account, if present.

    Methods
    -------
    tag : `str`
        The 4-digit tag of the user.
    mention : `str`
        The mentionable version of the user.
    """

    id: str | Snowflake = field(converter=Snowflake)
    """The ID of the user."""
    username: str = field()
    """The name of the user."""
    discriminator: str = field()
    """The discriminator (4-digit tag) of the user."""
    avatar: str | None = field(default=None)
    """The hash of the user's avatar."""
    bot: bool = field(default=False)
    """Whether the user is a bot or not."""
    system: bool = field(default=False)
    """Whether the user is from the official Discord System or not."""
    mfa_enabled: bool = field(default=False)
    """Whether the user has 2FA (two-factor authentication) enabled or not."""
    banner: str | None = field(default=None)
    """The hash of the user's banner, if present."""
    accent_color: int | None = field(default=None)
    """The color of the user's banner, if present."""
    locale: str | None = field(default=None)
    """The user's selected locale, if present."""
    verified: bool = field(default=True)
    """Whether the user has a verified e-mail or not."""
    email: str | None = field(default=None)
    """The e-mail associated to the user's account, if present."""
    flags: int | UserFlags = field(converter=UserFlags, default=0)
    """The public flags on the user's account, if present."""
    premium_type: int | UserPremiumType = field(converter=UserPremiumType, default=0)
    """The type of Nitro subscription the user has."""
    public_flags: int | UserFlags = field(converter=UserFlags, default=0)
    """The public flags on the user's account, if present."""

    @property
    def tag(self) -> str:
        """The 4-digit tag of the user."""
        return self.discriminator

    @property
    def mention(self) -> str:
        """The mentionable version of the user."""
        return f"<@{self.id}>"
