from ...const import MISSING


class _GuildEvents:
    """
    Acts as a lookup table for Gateway events relating to
    guilds from Discord.
    """

    @classmethod
    def lookup(cls, name: str) -> dict | MISSING:
        match name:
            case "GUILD_CREATE":
                return {"hello": "world"}
            case _:
                ...
