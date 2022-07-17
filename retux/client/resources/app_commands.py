from enum import IntEnum

from attrs import define, field

from .abc import Snowflake


@define(kw_only=True)
class ApplicationCommandOptionChoice:
    """
    Represents a choice in an option for an application command from Discord.

    Attributes
    ----------
    name : `str`
        The name of the application command option choice in-between 1-100 characters.
    name_localizations : `dict[str, str]`, optional
        The localised dictionary of names for the application command option choices, if present.
    value : `str`, `int`, optional
        The value of the application command option type. The maximum length is 100 characters if `STRING`.
    """

    name: str = field()
    """The name of the application command option choice in-between 1-100 characters."""
    name_localizations: dict[str, str] | None = field(converter=dict, default=None)
    """The localised dictionary of names for the application command option choices, if present."""
    value: str | int = field()
    """The value of the application command option type. The maximum length is 100 characters if `STRING`."""


class ApplicationCommandOptionType(IntEnum):
    """Represents the types of application command options from Discord."""

    SUB_COMMAND = 1
    """A subcommand or "nested command.\""""
    SUB_COMMAND_GROUP = 2
    """A subcommand group or "nest or nested commands.\""""
    STRING = 3
    """A string input."""
    INTEGER = 4
    """An integer input."""
    BOOLEAN = 5
    """A boolean input."""
    USER = 6
    """A user/guild member input. Guild member will take priority if user is in the server on execution."""
    CHANNEL = 7
    """A guild channel input."""
    ROLE = 8
    """A guild role input."""
    MENTIONABLE = 9
    """A mentionable resource input."""
    NUMBER = 10
    """A number input."""
    ATTACHMENT = 11
    """An attachment input for attachment resources."""


@define(kw_only=True)
class ApplicationCommandOption:
    """
    Represents an option in an application command from Discord.

    Attributes
    ----------
    type : `ApplicationCommandOptionType`
        The type of application command option.
    name : `str`
        The name of the option in-between 1-32 characters.
    name_localizations : `dict[str, str]`, optional
        The localised dictionary of names for the application command option, if present.
    description : `str`
        The description of the option in-between 1-100 characters.
    description_localizations : `dict[str, str]`, optional
        The localised dictionary of descriptions for the application command option, if present.
    required : `bool`, optional
        Whether the application command option is required to be entered or not.
    choices : `list[ApplicationCommandOptionChoice]`, optional
        Pre-filled choices of an application command option, if present.

        The choices must be from a `STRING`, `INTEGER` or `NUMBER` type.
        An application command option can have a maximum of 25 choices.
    options : `list[ApplicationCommandOption]`, optional
        The options of the application command, if present.
        Options are only present on `CHAT_INPUT` command types.

        These options will only show if this type is `SUB_COMMAND` or
        `SUB_COMMAND_GROUP`.
    min_value : `int`, optional
        The minimum value permitted for the application command option.
    max_value : `int`, optional
        The maximum value permitted for the application command option.
    min_length : `int`, optional
        The minimum length permitted for the application command option.
    max_length : `int`, optional
        The maximum length permitted for the application command option.
    autocomplete : `bool`, optional
        Whether the application command option is autocompleted or not.

        The option must be from a `STRING`, `INTEGER` or `NUMBER` type.
    """

    type: int | ApplicationCommandOptionType = field(
        converter=ApplicationCommandOptionType, default=None
    )
    """The type of application command option."""
    name: str = field()
    """The name of the option in-between 1-32 characters."""
    name_localizations: dict[str, str] | None = field(converter=dict, default=None)
    """The localised dictionary of names for the application command option, if present."""
    description: str = field()
    """The description of the option in-between 1-100 characters."""
    description_localizations: dict[str, str] | None = field(converter=dict, default=None)
    """The localised dictionary of descriptions for the application command option, if present."""
    required: bool | None = field(default=None)
    """Whether the application command option is required to be entered or not."""
    choices: list[ApplicationCommandOptionChoice] | None = field(converter=list, default=None)
    """
    Pre-filled selection choices of an application command option.

    The choices must be from a `STRING`, `INTEGER` or `NUMBER` type.
    An application command option can have a maximum of 25 choices.
    """
    options: list[dict] | list["ApplicationCommandOption"] | None = field(
        converter=list, default=None
    )
    """
    The options of the application command, if present.
    Options are only present on `CHAT_INPUT` command types.

    These options will only show if this type is `SUB_COMMAND` or
    `SUB_COMMAND_GROUP`.
    """

    # TODO: implement a channel type integer enumerable.
    # channel_types: list[ChannelType] | None = field(converter=list, default=None)
    # """The types of channels the option will filter to, if present."""

    min_value: int | None = field(default=None)
    """The minimum value permitted for the application command option."""
    max_value: int | None = field(default=None)
    """The maximum value permitted for the application command option."""
    min_length: int | None = field(default=None)
    """The minimum length permitted for the application command option. The minimum allowed is `0`."""
    max_length: int | None = field(default=None)
    """The maximum length permitted for the application command option. The maximum allowed is `1`."""
    autocomplete: bool | None = field(default=None)
    """
    Whether the application command option is autocompleted or not.

    The option must be from a `STRING`, `INTEGER` or `NUMBER` type.
    """


class ApplicationCommandType(IntEnum):
    """Represents the types of application commands from Discord."""

    CHAT_INPUT = 1
    """A chat-input command, or "slash command.\""""
    USER = 2
    """A user command, or "user context menu.\""""
    MESSAGE = 3
    """A message command, or "message context menu.\""""


@define(kw_only=True)
class ApplicationCommand:
    """
    Represents an application command from Discord.

    Attributes
    ----------
    id : `Snowflake`
        The ID of the application command.
    type : `ApplicationCommandType`
        The type of application command.
    application_id : `Snowflake`
        The ID of the application the command is under.
    guild_id : `Snowflake`, optional
        The ID of the guild the command is under, if present.
    name : `str`
        The name of the command in-between 1-32 characters.
    name_localizations : `dict[str, str]`, optional
        The localised dictionary of names for the application command, if present.
    description : `str`
        The description of the command in-between 1-100 characters.
        Descriptions are only present on `CHAT_INPUT` command types.
    description_localizations : `dict[str, str]`, optional
        The localised dictionary of descriptions for the application command, if present.
    options : `list[ApplicationCommandOption]`, optional
        The options of the application command, if present.
        A maximum of 25 options are allowed. Options are only
        present on `CHAT_INPUT` command types.
    default_member_permissions : `str`, optional
        The default permissions of the application command, if present.
    dm_permission : `bool`, optional
        Whether the application command is able to be ran in DMs or not.
    version : `Snowflake`, optional
        The internal version of application commands released. This auto-increments over time.
    """

    id: str | Snowflake = field(converter=Snowflake)
    """The ID of the application command."""
    type: int | ApplicationCommandType = field(converter=ApplicationCommandType)
    """The type of application command."""
    application_id: str | Snowflake = field(converter=Snowflake)
    """The ID of the application the command is under."""
    guild_id: str | Snowflake | None = field(converter=Snowflake, default=None)
    """The ID of the guild the command is under, if present."""
    name: str = field()
    """The name of the command in-between 1-32 characters."""
    name_localizations: dict[str, str] | None = field(converter=dict, default=None)
    """The localised dictionary of names for the application command, if present."""
    description: str = field()
    """
    The description of the command in-between 1-100 characters.
    Descriptions are only present on `CHAT_INPUT` command types.
    """
    description_localizations: dict[str, str] | None = field(converter=dict, default=None)
    """The localised dictionary of descriptions for the application command, if present."""
    options: list[dict] | list[ApplicationCommandOption] | None = field(
        converter=list, default=None
    )
    """
    The options of the application command, if present.
    A maximum of 25 options are allowed. Options are only
    present on `CHAT_INPUT` command types.
    """
    default_member_permissions: str | None = field(default=None)
    """The default permissions of the application command, if present."""
    dm_permission: bool | None = field(default=None)
    """Whether the application command is able to be ran in DMs or not."""
    version: str | Snowflake = field(converter=Snowflake)
    """The internal version of application commands released. This auto-increments over time."""
