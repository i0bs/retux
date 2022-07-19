from enum import IntEnum, IntFlag
from attrs import define, field
from retux.client.resources.abc import Snowflake


class ChannelType(IntEnum):
    GUILD_TEXT = 0
    """A text channel within a server."""
    DM = 1
    """A direct message between users."""
    GUILD_VOICE = 2
    """A voice channel within a server."""
    GROUP_DM = 3
    """A direct message between multiple users."""
    GUILD_CATEGORY = 4
    """An organizational category that contains up to 50 channels."""
    GUILD_NEWS = 5
    """A channel that users can follow and crosspost into their own server."""
    GUILD_NEWS_THREAD = 10
    """A temporary sub-channel within a GUILD_NEWS channel."""
    GUILD_PUBLIC_THREAD = 11
    """A temporary sub-channel within a GUILD_TEXT channel."""
    GUILD_PRIVATE_THREAD = 12
    """
    A temporary sub-channel within a GUILD_TEXT channel. 
    
    Only viewable by those invited and those with the MANAGE_THREADS permission
    """
    GUILD_STAGE_VOICE = 13
    """A voice channel for hosting events with an audience."""
    GUILD_DIRECTORY = 14
    """The channel in a hub containing the listed servers."""
    GUILD_FORUM = 15
    """A channel that can only contain threads."""


class VideoQualityMode(IntEnum):
    AUTO = 1
    """Discord chooses the quality for optimal performance."""
    FULL = 2
    """720p video resolution (1280x720)."""


class ChannelFlags(IntFlag):
    PINNED = 1 << 1
    """
    This thread is pinned to the top of its parent channel.
    
    Only available on forum channels.
    """


class MessageType(IntEnum):
    # TODO: find and document all of these
    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    USER_JOIN = 7
    GUILD_BOOST = 8
    GUILD_BOOST_TIER_1 = 9
    GUILD_BOOST_TIER_2 = 10
    GUILD_BOOST_TIER_3 = 11
    CHANNEL_FOLLOW_ADD = 12
    GUILD_DISCOVERY_DISQUALIFIED = 14
    GUILD_DISCOVERY_REQUALIFIED = 15
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING = 16
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING = 17
    THREAD_CREATED = 18
    REPLY = 19
    CHAT_INPUT_COMMAND = 20
    THREAD_STARTER_MESSAGE = 21
    GUILD_INVITE_REMINDER = 22
    CONTEXT_MENU_COMMAND = 23
    AUTO_MODERATION_ACTION = 24


class MessageActivityType(IntEnum):
    JOIN = 1
    SPECTATE = 2
    LISTEN = 3
    JOIN_REQUEST = 5


class MessageFlags(IntFlag):
    CROSSPOSTED = 1 << 0
    """This message has been published to subscribed channels."""
    IS_CROSSPOST = 1 << 1
    """This message originated from a message in another channel."""
    SUPPRESS_EMBEDS = 1 << 2
    """Do not include any embeds when serializing this message."""
    SOURCE_MESSAGE_DELETED = 1 << 3
    """The source message for this crosspost has been deleted."""
    URGENT = 1 << 4
    """This message came from the urgent message system."""
    HAS_THREAD = 1 << 5
    """This message has an associated thread, with the same id as the message."""
    EPHEMERAL = 1 << 6
    """This message is only visible to the user who invoked the Interaction."""
    LOADING = 1 << 7
    """This message is an Interaction Response showint that the bot is "thinking"."""
    FAILED_TO_MENTION_SOME_ROLES_IN_THREAD = 1 << 8
    """This message failed to mention some roles and add their members to the thread."""


@define()
class Overwrite:
    """
    Represents a permission overwrite from Discord.

    Attributes
    ----------
    id : `Snowflake`
        The ID of the Role or user.
    type : `int`
        The type of overwrite.

        User 0 for to overwrite a role permission and 1 to overwrite a member permission.
    allow : `str`
        The bit set representing the overwrite's allowed permissions.
    deny : `str`
        The bit set representing the overwrite's denied permissions.
    """

    id: str | Snowflake = field(converter=Snowflake)
    """The ID of the Role or user."""
    type: int = field()
    """
    The type of overwrite.

    Use `0` for to overwrite a role's permission and `1` to overwrite a guild member's permission.
    """
    allow: str = field()
    """The bit set representing the overwrite's allowed permissions."""
    deny: str = field()
    """The bit set representing the overwrite's denied permissions."""


@define()
class MessageActivity:
    """
    Represents a message activity structure from Discord.

    Attributes
    ----------
    type : `int`
        The type of message activity.
    party_id : `Snowflake`, optional
        The party_id from a rich presence event.
    """

    type: int | MessageActivityType = field(converter=MessageActivityType)
    """The type of message activity."""
    party_id: str | Snowflake | None = field(default=None, converter=Snowflake)
    """The party_id from a rich presence event."""


@define()
class FollowedChannel:
    """
    Represents a followed channel from Discord.

    Attributes
    ----------
    channel_id : `Snowflake`
        The ID of the source channel.
    webhook_id : `Snowflake`
        The ID of the created target webhook.
    """

    channel_id: str | Snowflake = field(converter=Snowflake)
    """The ID of the source channel."""
    webhook_id: str | Snowflake = field(converter=Snowflake)
    """The ID of the created target webhook."""


@define()
class Channel:
    """
    Represents a Channel from Discord.

    Attributes
    ----------
    id : `Snowflake`
        The ID of the channel.
    type : `ChannelType`
        The type of the channel.
    guild_id : `Snowflake`, optional
        The ID of the guild. Optional because it can be missing in gateway events.
    position : `int`, optional
        Sorted position of the channel.
    permission_overwrites : `list[Overwrite]`, optional
        Explicit permission overwrites for members and roles.
    name : `str`, optional
        The name of the channel.

        A channel name can be between 1 and 100 characters.
    topic : `str`, optional
        The topic of the channel.

        A channel tpic can be between 1 and 1024 characters.
    nsfw : `bool`, optional
        Whether or not the channel is nsfw. Defaults to False.
    last_message_id : `Snowflake`, optional
        The ID of the last message sent in this channel

        Can also be a thread if the channel is a forum. May not be an existing or valid message or thread.
    bitrate : `int`, optional
        The bitrate of the voice channel.
    user_limit : `int`, optional
        The user limit of the voice channel.
    rate_limit_per_user : `int`, optional
        Amount of seconds a user has to wait before sending another message

        Can be a number up to 21600. Bots, as well as users with the permission manage_messages or manage_channel, are unaffected.
    recipients : `list[User]`, optional
        The recipients of the dm.
    icon : `str`, optional
        The hash for the channel's icon.
    owner_id : `Snowflake`, optional
        The ID of the creator of the group dm or thread.
    application_id : `Snowflake`, optional
        The ID of the application that created the dm if it is bot-created.
    parent_id : `Snowflake`, optional
        The ID of the parent of the channel

        Represents the parent category for regular channels and the parent channel for threads.
    last_pin_timestamp : `str`, optional
        The time when the last message was pinned.
    rtc_region : `str`, optional
        Voice region id for the voice channel, automatic when set to null.
    video_quality_mode : `VideoQualityMode`, optional
        The video quality mode of the voice channel.
    message_count : `int`, optional
        An approximate count of messages in a thread.

        Stops counting at 50.
    member_count : `int`, optional
        An approximate count of messages in a thread.

        Stops counting at 50.
    thread_metadata : `ThreadMetadata`, optional
        Thread-specific fields not needed by other channels.
    member : `ThreadMember`, optional
        Thread member object for the current user if they have joined the thread

        This is only included on certain api endpoints.
    default_auto_archive_duration : `int`, optional
        Default archive duration for clients in minutes.

        Can be set to 60, 1440, 4320, 10080.
    permissions : `str`, optional
        Computed permissions for the invoking user in the channel, including overwrites.

        Only included when part of the resolved data received on a slash command interaction.
    flags : `ChannelFlags`, optional
        Channel flags combined as a bitfield.
    """

    id: str | Snowflake = field(converter=Snowflake)
    """The ID of the channel."""
    type: int | ChannelType = field(converter=ChannelType)
    """The type of the channel."""
    guild_id: str | Snowflake | None = field(default=None, converter=Snowflake)
    """The ID of the guild. Optional because it can be missing in gateway events."""
    position: int | None = field(default=None)
    """Sorted position of the channel."""
    permission_overwrites: list[dict] | list[Overwrite] | None = field(
        default=None, converter=dict
    )
    """Explicit permission overwrites for members and roles."""
    name: str | None = field(default=None)
    """
    The name of the channel. 
    
    A channel name can be between 1 and 100 characters.
    """
    topic: str | None = field(default=None)
    """
    The topic of the channel.

    A channel tpic can be between 1 and 1024 characters.
    """
    nsfw: bool | None = field(default=False)
    """Whether or not the channel is nsfw. Defaults to False."""
    last_message_id: str | Snowflake | None = field(default=None, converter=Snowflake)
    """
    The ID of the last message sent in this channel
    
    Can also be a thread if the channel is a forum. May not be an existing or valid message or thread.
    """
    bitrate: int | None = field(default=None)
    """The bitrate of the voice channel."""
    user_limit: int | None = field(default=None)
    """The user limit of the voice channel."""
    rate_limit_per_user: int | None = field(default=None)
    """
    Amount of seconds a user has to wait before sending another message
    
    Can be a number up to 21600. Bots, as well as users with the permission manage_messages or manage_channel, are unaffected.
    """
    recipients: list[dict] | list[User] | None = field(default=None, converter=dict)
    """The recipients of the dm."""
    icon: str | None = field(default=None)
    """The hash for the channel's icon."""
    owner_id: str | Snowflake | None = field(default=None, converter=Snowflake)
    """The ID of the creator of the group dm or thread."""
    application_id: str | Snowflake | None = field(default=None, converter=Snowflake)
    """The ID of the application that created the dm if it is bot-created."""
    parent_id: str | Snowflake | None = field(default=None, converter=Snowflake)
    """
    The ID of the parent of the channel

    Represents the parent category for regular channels and the parent channel for threads.
    """
    last_pin_timestamp: str | None = field(default=None)
    """The time when the last message was pinned."""
    rtc_region: str | None = field(default=None)
    """The channel's voice region ID if present, set to automatic when left as `None`."""
    video_quality_mode: int | VideoQualityMode | None = field(
        default=None, converter=VideoQualityMode
    )
    """The video quality mode of the voice channel."""
    message_count: int | None = field(default=None)
    """"
    An approximate count of messages in a thread.

    Stops counting at 50.
    """
    member_count: int | None = field(default=None)
    """
    An approximate count of users in a thread.

    Stops counting at 50.
    """
    thread_metadata: dict | ThreadMetadata | None = field(
        default=None, converter=ThreadMetadata
    )
    """Thread-specific fields not needed by other channels."""
    member: ThreadMember | None = field(default=None)
    """
    The thread member representation of the user if they have joined the thread.
        
    This is only included on certain api endpoints.
    """
    default_auto_archive_duration: int | None = field(default=None)
    """
    The default archive duration for threads in minutes.
    
    Can be set to `60`, `1440`, `4320`, `10080`.
    """
    permissions: str | None = field(default=None)
    """
    The computed permissions for the invoking user in the channel, including any overwrites.
        
    Only included when part of the resolved data received on a slash command interaction.
    """
    flags: int | ChannelFlags | None = field(default=None, converter=ChannelFlags)
    """Channel flags combined as a bitfield."""
