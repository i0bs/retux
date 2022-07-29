from enum import IntEnum
from attrs import define, field
from .abc import Object, Snowflake
from .user import User
from ...utils.converters import list_c, optional_c


class StickerType(IntEnum):
    """
    Represents the types of stickers from Discord.
    
    Constants
    ---------
    STANDARD
        An official sticker of a pack. 
    
        Only availible with Nitro unless
        part of a removed purchaseable pack.
    GUILD
        A sticker uploaded by a guild.
    """
    STANDARD = 1
    """
    An official sticker of a pack. 
    
    Only availible with Nitro unless
    part of a removed purchaseable pack.
    """
    GUILD = 2
    """A sticker uploaded by a guild."""


class StickerFormatType(IntEnum):
    """
    Represents the types of sticker formats from Discord.
    
    Constants
    ---------
    PNG
        A sticker formatted with the `.png` format.
    APNG
        A sticker formatted with the `.apng` format.
    LOTTIE
        A sticker formatted with the `.lottie` format.
    """
    PNG = 1
    """A sticker formatted with the `.png` format."""
    APNG = 2
    """A sticker formatted with the `.apng` format."""
    LOTTIE = 3
    """A sticker formatted with the `.lottie` format."""


@define(kwargs_only=True)
class Sticker(Object):
    """
    Represents a sticker from Discord.

    Attributes
    ----------
    id : `Snowflake`
        The ID of the sticker.
    pack_id : `Snowflake`, optional
        The ID of the pack containing the sticker.

        Only standard stickers owned by Discord
        can be part of a sticker pack.
    name : `str`
        The name of the sticker.
    description : `str`, optional
        The description of the sticker.
    tags : `str`
        The tags or emoji equivelent of a sticker.

        If the sticker is a standard sticker, this
        field will be a comma seperated list of 
        keywords. If the sticker is guild owned, it
        will be the name of an emoji.
    asset : `str`
        An empty string previously for the sticker asset hash.
    type : `StickerType`
        The type of the sticker.
    format_type : `StickerFormatType`
        The formatting type that the sticker uses.
    available : `bool`, optinal
        Whether or not the sticker is availible.

        May be false if the guild that owns it
        has lost a level of boosting.
    guild_id : `Snowflake`, optional
        The ID of the guild that owns the sticker.

        Will only be set to None if the sticker is
        owned by Discord.
    user : `User`, optional
        The user that uploaded the sticker.

        Will only be set to None if the sticker is
        owned by Discord.
    sort_value : `int`, optional
        The sticker's order within its sticker pack.

        Will only be availible if the sticker is
        part of a pack and owned by Discord.
    """
    id: str | Snowflake = field(converter=Snowflake)
    """The ID of the sticker."""
    pack_id: str | Snowflake | None = field(converter=optional_c(Snowflake), default=None)
    """
    The ID of the pack containing the sticker.
    
    Only standard stickers owned by Discord
    can be part of a sticker pack.
    """
    name: str = field()
    """The name of the sticker."""
    description: str | None = field(default=None)
    """The description of the sticker."""
    tags: str = field()
    """
    The tags or emoji equivelent of a sticker.
    
    If the sticker is a standard sticker, this
    field will be a comma seperated list of 
    keywords. If the sticker is guild owned, it
    will be the name of an emoji.
    """
    asset: str = field(default="")
    """An empty string previously for the sticker asset hash."""
    type: int | StickerType = field(converter=StickerType)
    """The type of the sticker."""
    format_type: int | StickerFormatType = field(converter=StickerFormatType)
    """The formatting type that the sticker uses."""
    available: bool | None = field(default=None)
    """
    Whether or not the sticker is availible.
    
    May be false if the guild that owns it
    has lost a level of boosting.
    """
    guild_id: str | Snowflake | None = field(converter=optional_c(Snowflake))
    """
    The ID of the guild that owns the sticker.
    
    Will only be set to None if the sticker is
    owned by Discord.
    """
    user: dict | User | None = field(converter=optional_c(User), default=None)
    """
    The user that uploaded the sticker.
    
    Will only be set to None if the sticker is
    owned by Discord.
    """
    sort_value: int | None = field(default=None)
    """
    The sticker's order within its sticker pack.

    Will only be availible if the sticker is
    part of a pack and owned by Discord.
    """


@define(kwargs_only=True)
class StickerItem(Object):
    """
    Represents the bare information needed 
    to begin loading a sticker from Discord.
    
    Attributes
    ----------
    id : `Snowflake`
        The ID of the sticker being represented.
    name : `str`
        The name of the sticker being represented.
    format_type : `StickerFormatType`
        The type of formatting of the sticker being represented.
    """
    id: str | Snowflake = field(converter=Snowflake)
    """The ID of the sticker being represented."""
    name: str = field()
    """The name of the sticker being represented."""
    format_type: int | StickerFormatType = field(converter=StickerFormatType)
    """The type of formatting of the sticker being represented."""


@define(kwargs_only=True)
class StickerPack(Object):
    """
    Represents a sticker pack from Discord.

    Attributes
    ----------
    id : `Snowflake`
        The ID of the sticker pack.
    stickers : `list[Sticker]`
        The stickers within the sticker pack.
    name : `str
        The name of the sticker pack.
    sku_id : `Snowflake`
        The ID of the pack's SKU.
    cover_sticker_id : `Snowflake`, optional
        The ID of the sticker featured as the pack's icon.
    description : `str`
        The description of the sticker pack.
    banner_asset_id : `Snowflake`, optional
        The ID of the sticker packs's banner image.
    """
    id: str | Snowflake = field(converter=Snowflake)
    """The ID of the sticker pack."""
    stickers: list[dict] | list[Sticker] = field(list_c(Sticker))
    """The stickers within the sticker pack."""
    name: str = field()
    """The name of the sticker pack."""
    sku_id: str | Snowflake = field(converter=Snowflake)
    """The ID of the pack's SKU."""
    cover_sticker_id: str | Snowflake | None = field(converter=optional_c(Snowflake), default=None)
    """The ID of the sticker featured as the pack's icon."""
    description: str = field()
    """The description of the sticker pack."""
    banner_asset_id: str | Snowflake | None = field(converter=optional_c(Snowflake))
    """The ID of the sticker packs's banner image."""