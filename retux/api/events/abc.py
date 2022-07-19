from attrs import define, field

from ...const import MISSING


@define()
class Event:
    """
    Represents the base information of a Gateway event from Discord.

    Attributes
    ----------
    _name : `str`
        The name of the Gateway event.
    _bot : `Bot`, optional
        The bot instance linked to the event. This is added on so
        that we can hook into the instance's calls for callbacks
        related to the event, as well as potential HTTP calls.

        When left blank, this event represents purely receive-only
        information with no possible sending traits.
    """

    _name: str = field()
    """The name of the Gateway event."""
    _bot: "Bot" | MISSING = field(default=MISSING)  # noqa
    """
    The bot instance linked to the event. This is added on so
    that we can hook into the instance's calls for callbacks
    related to the event, as well as potential HTTP calls.

    When left blank, this event represents purely receive-only
    information with no possible sending traits.
    """
