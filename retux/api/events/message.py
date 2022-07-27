from ...const import MISSING


class _MessageEvents:
    """
    Acts as a lookup table for Gateway events relating to
    messages from Discord.
    """

    @classmethod
    def lookup(cls, name: str, data: dict) -> dict | MISSING:
        match name:
            case "MESSAGE_CREATE":
                ...
            case "MESSAGE_UPDATE":
                ...
            case "MESSAGE_DELETE":
                ...
            case "MESSAGE_DELETE_BULK":
                ...
            case "MESSAGE_REACTION_ADD":
                ...
            case "MESSAGE_REACTION_REMOVE":
                ...
            case "MESSAGE_REACTION_REMOVE_ALL":
                ...
            case "MESSAGE_REACTION_REMOVE_EMOJI":
                ...
            case _:
                ...
