from enum import IntFlag


class Intents(IntFlag):
    """
    Intents, otherwise known as "Gateway intents" are a set of
    bitwise values that help control the computational burden
    received by a Gateway client.

    ---

    Some intents in this class are documented as being "privileged,"
    a special intent that must be approved before receiving access
    to its respective data. In order to do this, the application in
    question (e.g. a bot) must have the intent enabled through
    the Developer Portal settings of said application.

    The following intents have this label:

    - `GUILD_PRESENCES` - event(s) relating to a guild member's presence.
    - `GUILD_MEMBERS` - event(s) relating to a guild member.
    - `MESSAGE_CONTENT` - event(s) relating to the `content`, `embeds`, `attachments` or `components` fields of an object with said limitation.

    Additionally, you are able to access all of these with `PRIVILEGED`.

    ---

    A bot should never have intents that will ultimately
    be discarded or unused. Please see all intents given. `ALL`
    may be used but must be acknowledged for carrying every
    intent given by this class.
    """

    GUILDS = 1 << 0
    """
    `GUILDS` controls a majority of events shown for any guild a bot is in.
    The following events are gated behind this intent:

    - `GUILD_CREATE` - upon joining a guild.
    - `GUILD_UPDATE` - upon a guild updating data.
    - `GUILD_DELETE` - upon leaving a guild.
    - `GUILD_ROLE_CREATE` - upon a role in a guild being created.
    - `GUILD_ROLE_UPDATE` - upon a role's data in a guild being updated.
    - `GUILD_ROLE_DELETE` - upon a rolei n a guild being deleted.
    - `CHANNEL_CREATE` - upon a channel in a guild being created.
    - `CHANNEL_UPDATE` - upon a channel's data in a guild being updated.
    - `CHANNEL_DELETE` - upon a channel in a guild being deleted.
    - `CHANNEL_PINS_UPDATE` - upon a pin in a channel being created, updated or deleted.
    - `THREAD_CREATE` - upon a thread in a guild being created, or the bot added to one.
    - `THREAD_UPDATE` - upon a thread in a guild being updated. This event sometimes coincides with `THREAD_CREATE`.
    - `THREAD_DELETE` - upon a thread in a guild being deleted.
    - `THREAD_LIST_SYNC` - upon a thread in a guild updating its member list. This event ultimately follows `THREAD_UPDATE`.
    - `THREAD_MEMBER_UPDATE` - upon a member in a guild thread being updated.
    - `THREAD_MEMBERS_UPDATE` - upon a set of members in a guild thread being updated. This event ultimately follows `THREAD_UPDATE`.
    - `STAGE_INSTANCE_CREATE` - upon a stage event in a guild being created.
    - `STAGE_INSTANCE_UPDATE` - upon a stage event's data in a guild being updated.
    - `STAGE_INSTANCE_DELETE` - upon a stage event in a guild being deleted.
    """
    GUILD_MEMBERS = 1 << 1
    """
    This intent is considered to be "privileged." Please see the documentation
    on the main class (`Intents`) to learn more.

    `GUILD_MEMBERS` controls events for a guild member's data being shown.
    The following events are gated behind this intent:

    - `GUILD_MEMBER_ADD` - upon a member being added to a guild.
    - `GUILD_MEMBER_UPDATE` - upon a member's data in a guild being updated.
    - `GUILD_MEMBER_REMOVE` - upon a member being removed from a guild.
    - `THREAD_MEMBERS_UPDATE` - Coinciding with the `GUILDS` intent. (see)
    """
    GUILD_BANS = 1 << 2
    """
    `GUILD_BANS` controls events for a guild member's ban state.
    The following events are gated behind this intent:

    - `GUILD_BAN_ADD` - upon a member being banned from a guild. `GUILD_MEMBER_REMOVE` ultimately follows this.
    - `GUILD_BAN_REMOVE` - upon a member being unbanned from a guild.
    """
    GUILD_EMOJIS_AND_STICKERS = 1 << 3
    """
    `GUILD_EMOJIS_AND_STICKERS` controls events for emojis and stickers
    being sent. The following events are gated behind this intent:

    - `GUILD_EMOJIS_UPDATE` - upon an emoji or set being updated in a guild.
    - `GUILD_STICKERS_UPDATE` - upon a sticker or set being updated in a guild.
    """
    GUILD_INTEGRATIONS = 1 << 4
    """
    `GUILD_INTEGRATIONS` controls events for integrations.
    The following events are gated behind this intent:

    - `GUILD_INTEGRATIONS_UPDATE` - upon an integration or set being updated in a guild.
    - `INTEGRATION_CREATE` - upon an integration regardless of guild status being created.
    - `INTEGRATION_UPDATE` - upon an integration regardless of guild status being updated.
    - `INTEGRATION_DELETE` - upon an integration regardless of guild status being deleted.
    """
    GUILD_WEBHOOKS = 1 << 5
    """
    `GUILD_WEBHOOKS` controls an event for webhooks in a guild.
    The following event is gated behind this intent:

    - `WEBHOOKS_UPDATE` - upon a webhook in a guild being updated.
    """
    GUILD_INVITES = 1 << 6
    """
    `GUILD_INVITES` controls events for invites in a guild.
    The following events are gated behind this intent:

    - `INVITE_CREATE` - upon a guild invitation being created.
    - `INVITE_DELETE` - upon a guild invitation being deleted.
    """
    GUILD_VOICE_STATES = 1 << 7
    """
    `GUILD_VOICE_STATES` controls an event for a guild member's voice state.
    The following event is gated behind this intent:

    - `VOICE_STATE_UPDATE` - upon a guild member's voice state being updated.
    """
    GUILD_PRESENCES = 1 << 8
    """
    This intent is considered to be "privileged." Please see the documentation
    on the main class (`Intents`) to learn more.

    `GUILD_PRESENCES` controls an event for a guild member's presence.
    The following event is gated behind this intent:

    - `PRESENCE_UPDATE` - upon a guild member's presence being updated.
    """
    GUILD_MESSAGES = 1 << 9
    """
    `GUILD_MESSAGES` controls events for messages in a guild.
    The following events are gated behind this intent:

    - `MESSAGE_CREATE` - upon a message in a guild being created.
    - `MESSAGE_UPDATE` - upon a message in a guild being updated.
    - `MESSAGE_DELETE` - upon a message in a guild being deleted.
    - `MESSAGE_DELETE_BULK` - upon a set of messages in a guild being deleted.
    """
    GUILD_MESSAGE_REACTIONS = 1 << 10
    """
    `GUILD_MESSAGE_REACTIONS` controls events for reactions on a guild message.
    The following events are gated behind this intent:

    - `MESSAGE_REACTION_ADD` - upon a reaction on a guild message being added.
    - `MESSAGE_REACTION_REMOVE` - upon a reaction on a guild message being removed.
    - `MESSAGE_REMOVE_ALL` - upon a guild member with the "Manage Messages" permission removing all reactions on a guild message.
    - `MESSAGE_REMOVE_EMOJI` - ???
    """
    GUILD_MESSAGE_TYPING = 1 << 11
    """
    `GUILD_MESSAGE_TYPING` controls an event for a guild member typing.
    The following event is gated behind this intent:

    - `TYPING_START` - upon a guild member typing in a guild.
    """
    DIRECT_MESSAGES = 1 << 12
    """
    `DIRECT_MESSAGES` controls events for direct messages.
    The following events are the same as `GUILD_MESSAGES`, with the exception of:

    - `CHANNEL_PINS_UPDATE` - upon a set of pins in a guild channel being updated.
    """
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    """
    `DIRECT_MESSAGE_REACTIONS` controls events for reactions on a direct message.
    The following events are the same as `GUILD_MESSAGE_REACTIONS`.
    """
    DIRECT_MESSAGE_TYPING = 1 << 14
    """
    `DIRECT_MESSAGE_TYPING` controls an event for a user typing.
    The following event is the same as `GUILD_MESSAGE_TYPING`.
    """
    MESSAGE_CONTENT = 1 << 15
    """
    This intent is considered to be "privileged." Please see the documentation
    on the main class (`Intents`) to learn more.

    `MESSAGE_CONTENT` controls data passed to these specific fields
    in objects when specified:
    - `content` - data of the exact contents given on a message.
    - `embeds` - an embed or set on a message.
    - `attachments` - an attachment or set on a message.
    - `components` - a component or set on a message.
    """
    GUILD_SCHEDULED_EVENTS = 1 << 16
    """
    `GUILD_SCHEDULED_EVENTS` controls events for scheduled events in a guild.
    The following events are gated behind this intent:

    - `GUILD_SCHEDULED_EVENT_CREATE` - upon a scheduled event in a guild being created.
    - `GUILD_SCHEDULED_EVENT_UPDATE` - upon a scheduled event in a guild being updated.
    - `GUILD_SCHEDULED_EVENT_DELETE` - upon a scheduled event in a guild being deleted.
    - `GUILD_SCHEDULED_EVENT_USER_ADD` - upon a guild member in a scheduled event being added.
    - `GUILD_SCHEDULED_EVENT_USER_REMOVE` - upon a guild member in a scheduled event being removed.
    """
    AUTO_MODERATION_CONFIGURATION = 1 << 20
    """
    `AUTO_MODERATION_CONFIGURATION` controls events for settings of a guild's AutoMod.
    The following events are gated behind this intent:

    - `AUTO_MODERATION_RULE_CREATE` - upon an automoderation rule being created.
    - `AUTO_MODERATION_RULE_UPDATE` - upon an automoderation rule being updated.
    - `AUTO_MODERATION_RULE_DELETE` - upon an automoderation rule being deleted.
    """
    AUTO_MODERATION_EXECUTION = 1 << 21
    """
    `AUTO_MODERATION_EXECUTION` controls an event for executing AutoMod rules.
    The following event is gated behind this intent:

    - `AUTO_MODERATION_ACTION_EXECUTION` - upon an automoderation rule or set being executed.
    """

    PRIVILEGED = GUILD_PRESENCES | GUILD_MEMBERS | MESSAGE_CONTENT
    """
    `PRIVILEGED` is the culmination of all privileged intents.
    The following intents are known to be "privileged:"

    - `GUILD_PRESENCES`
    - `GUILD_MEMBERS`
    - `MESSAGE_CONTENT`
    """
    NON_PRIVILEGED = (
        GUILDS
        | GUILD_BANS
        | GUILD_EMOJIS_AND_STICKERS
        | GUILD_INTEGRATIONS
        | GUILD_WEBHOOKS
        | GUILD_INVITES
        | GUILD_VOICE_STATES
        | GUILD_MESSAGES
        | GUILD_MESSAGE_TYPING
        | DIRECT_MESSAGES
        | DIRECT_MESSAGE_TYPING
        | DIRECT_MESSAGE_REACTIONS
        | GUILD_SCHEDULED_EVENTS
        | AUTO_MODERATION_CONFIGURATION
        | AUTO_MODERATION_EXECUTION
    )
    """
    `NON_PRIVILEGED` is the culmination of all intents that are not
    "privileged." See `PRIVILEGED` for the missing intents.
    """
    ALL = PRIVILEGED | NON_PRIVILEGED
    """
    `ALL` is the culmination of all intents of this class.

    If necessary, see `PRIVILEGED` and `NON_PRIVILEGED` for their inclusion.
    """
