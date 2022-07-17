from enum import IntEnum

from attrs import define, field

from .abc import Component


class ComponentType(IntEnum):
    """
    Represents the types of components from Discord.

    Constants
    ---------
    ACTION_ROW
        An action row, used in `ActionRow`.
    BUTTON
        A button, used in `Button`.
    SELECT_MENU
        A select menu, used in `SelectMenu`.
    TEXT_INPUT
        A text input, used in `TextInput`.
    """

    ACTION_ROW = 1
    """An action row, used in `ActionRow`."""
    BUTTON = 2
    """A button, used in `Button`."""
    SELECT_MENU = 3
    """A select menu, used in `SelectMenu`."""
    TEXT_INPUT = 4
    """A text input, used in `TextInput`."""


@define(kw_only=True)
class ActionRow(Component):
    """
    Represents an action row component from Discord.

    ---

    An action row may only have 5 components stored in it.
    It may not be nested inside of itself or
    contain itself.

    ---

    Attributes
    ----------
    type : `ComponentType`
        The type of component, as `ComponentType.ACTION_ROW`.
    components : `list[Component]`
        The components stored under the action row.
    """

    type: int | ComponentType = field(converter=ComponentType, default=ComponentType.ACTION_ROW)
    """The type of component, as `ComponentType.ACTION_ROW`."""
    components: list[Component] = field(converter=list, default=None)
    """The components stored in the action row."""


class ButtonStyle(IntEnum):
    """
    Represents the styles of buttons from Discord.

    ---

    See `Button` for information regarding the use of styles.

    ---

    Constants
    ---------
    PRIMARY (BLUE)
        A "CTA" indication.
    SECONDARY (GREY)
        A secondary usage indication.
    SUCCESS (GREEN)
        A successful indication.
    DANGER (RED)
        A dangerous or destructive indication.
    LINK (URL)
        An navigation indication.
    """

    PRIMARY = 1
    """A \"CTA\" indication."""
    SECONDARY = 2
    """A secondary usage indication."""
    SUCCESS = 3
    """A successful indication."""
    DANGER = 4
    """A dangerous or destructive indication."""
    LINK = 5
    """An navigation indication."""

    # These are just aliases of the button styles.
    BLUE = 1
    """An alias of `PRIMARY`."""
    GREY = 2
    """An alias of `SECONDARY`."""
    GREEN = 3
    """An alias of `SUCCESS`."""
    RED = 4
    """An alias of `DANGER`."""
    URL = 5
    """An alias of `LINK`."""


@define(kw_only=True)
class Button(Component):
    """
    Represents a button component from Discord.

    ---

    To use a style that indicates anything besides a navigation path,
    (or essentially a colour) you must have the `custom_id` attribute
    filled in your component. The `url` attribute is not allowed.

    For a link, the `url` attribute must be present without `custom_id`.

    ---

    Attributes
    ----------
    type : `ComponentType`
        The type of component, as `ComponentType.BUTTON`.
    style : `ButtonStyle`
        The style of the button. Please see `Button` for usage.
    label : `str`, optional
        The labelled contents of the button. The maximum
        length is 80 characters.
    custom_id : `str`, optional
        A customisable identifiable descriptor for the button.
    url : `str`, optional
        The URL relating to the button.
    disabled : `bool`
        Whether the button is disabled for usage or not. Defaults to `False`.
    """

    type: int | ComponentType = field(converter=ComponentType, default=ComponentType.BUTTON)
    """The type of component, as `ComponentType.BUTTON`."""
    style: int | ButtonStyle = field(converter=ButtonStyle)
    """The style of the button. Please see `Button` for usage."""
    label: str | None = field(default=None)
    """The labelled contents of the button. The maximum length is 80 characters."""

    # TODO: implement a partial emoji abc.
    # emoji: dict | PartialEmoji | None = field(converter=PartialEmoji, default=None)
    # """The emoji related to the button, if present."""

    custom_id: str | None = field(default=None)
    """A customisable identifiable descriptor for the button."""
    url: str | None = field(default=None)
    """The URL relating to the button."""
    disabled: bool = field(default=False)
    """Whether the button is disabled for usage or not. Defaults to `False`."""


@define(kw_only=True)
class SelectOption:
    """
    Represents an option in a select menu from Discord.

    Attributes
    ----------
    label : `str`
        The labelled contents of the select option.
        The maximum length is 80 characters.
    value : `str`
        The value of the select option.
    description : `str`, optional
        An additional description of the select option, if present.
    default : `bool`
        Whether the select option is chosen by default or not.
        Defaults to `False`.
    """

    label: str = field()
    """The label of the select option."""
    value: str = field()
    """The value of the select option."""
    description: str | None = field(default=None)
    """An additional description of the select option, if present."""

    # TODO: implement a partial emoji abc.
    # emoji: dict | PartialEmoji | None = field(default=None)
    # """The emoji related to the select option, if present."""

    default: bool = field(default=False)
    """Whether the select option is chosen by default or not. Defaults to `False`."""


@define(kw_only=True)
class SelectMenu(Component):
    """
    Represents a select menu component from Discord.

    Attributes
    ----------
    type : `ComponentType`
        The type of component, as `ComponentType.SELECT_MENU`.
    custom_id : `str`
        A customisable identifiable descriptor for the select menu.
    options : `list[SelectOption]`
        The options of the select menu.
    placeholder : `str`, optional
        The placeholder text of the select menu, if present.
    min_values : `int`
        The minimum number of options needed for the menu in-between 0-25.
        Defaults to `1`.
    max_values : `int`
        The maximum number of options needed for the menu in-between 1-25.
        Defaults to `1`.
    disabled : `bool`
        Whether the select menu is disabled for usage or not. Defaults
        to `False`.
    """

    type: int | ComponentType = field(converter=ComponentType, default=ComponentType.SELECT_MENU)
    """The type of component, as `ComponentType.SELECT_MENU`."""
    custom_id: str = field()
    """A customisable identifiable descriptor for the select menu."""
    options: list[SelectOption] = field(converter=list)
    """The options of the select menu."""
    placeholder: str | None = field(default=None)
    """The placeholder text of the select menu, if present."""
    min_values: int = field(default=1)
    """
    The minimum number of options needed for the menu
    in-between 0-25. Defaults to `1`.
    """
    max_values: int = field(default=1)
    """
    The maximum number of options needed for the menu
    in-between 1-25. Defaults to `1`.
    """
    disabled: bool = field(default=False)
    """Whether the select menu is disabled for usage or not. Defaults to `False`."""


class TextInputStyle(IntEnum):
    """
    Represents the styles of text inputs from Discord.

    Constants
    ---------
    SHORT
        A short-form/single-line input.
    PARAGRAPH
        A long-form/multi-line input.
    """

    SHORT = 1
    """A short-form/single-line input."""
    PARAGRAPH = 2
    """A long-form/multi-line input."""


@define(kw_only=True)
class TextInput(Component):
    """
    Represents a text input component from Discord.

    Attributes
    ----------
    type : `ComponentType`
        The type of component, as `ComponentType.TEXT_INPUT`.
    custom_id : `str`
        A customisable identifiable descriptor for the text input.
    style : `TextInputStyle`
        The style of the text input.
    label : `str`
        The labelled contents of the modal. The maximum length is 45 characters.
    min_length : `int`, optional
        The minimum allowed length for a text input in-between
        1-4000 characters. Defaults to `0`.
    max_length : `int`, optional
        The maximum allowed length for a text input in-between
        1-4000 characters. Defaults to `1`.
    required : `bool`, optional
        Whether the text input is required to be filled or not. Defaults to `True`.
    value : `str`, optional
        A pre-filled value for the text input, if present.
        The maximum length is 4000 characters.
    placeholder : `str`, optional
        The placeholder text of the text input, if present.
        The maximum length is 100 characters.
    """

    type: int | ComponentType = field(converter=ComponentType, default=ComponentType.TEXT_INPUT)
    """The type of component, as `ComponentType.TEXT_INPUT`."""
    custom_id: str = field()
    """A customisable identifiable descriptor for the text input."""
    style: int | TextInputStyle = field(converter=TextInputStyle)
    """The style of the text input."""
    label: str = field()
    """The labelled contents of the modal. The maximum length is 45 characters."""
    min_length: int = field(default=0)
    """
    The minimum allowed length for a text input in-between
    1-4000 characters. Defaults to `0`.
    """
    max_length: int = field(default=1)
    """
    The maximum allowed length for a text input in-between
    1-4000 characters. Defaults to `1`.
    """
    required: bool = field(default=True)
    """Whether the text input is required to be filled or not. Defaults to `True`."""
    value: str | None = field(default=None)
    """A pre-filled value for the text input, if present. The maximum length is 4000 characters."""
    placeholder: str | None = field(default=None)
    """The placeholder text of the text input, if present. The maximum length is 100 characters."""


@define(kw_only=True)
class Modal(Component):
    """
    Represents a modal component from Discord.

    Attributes
    ----------
    title : `str`
        The title of the modal.
    custom_id : `str`
        A customisable identifiable descriptor for the modal.
    components : `list[TextInput]`
        The components stored in the modal.
    """

    title: str = field()
    """The title of the modal."""
    custom_id: str = field()
    """A customisable identifiable descriptor for the modal."""
    components: list[TextInput] = field(converter=list)
    """The components stored in the modal."""
